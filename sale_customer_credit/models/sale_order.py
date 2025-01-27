from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError, UserError


logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_paid_via_transaction = fields.Boolean(
        string="Paid via Transaction",
        compute="_compute_is_paid_via_transaction",
        store=True
    )

    @api.depends('transaction_ids.state', 'transaction_ids.amount', 'amount_total', 'transaction_ids.payment_method_code')
    def _compute_is_paid_via_transaction(self):
        for order in self:
            order.is_paid_via_transaction = any(
                tx.state == 'done' and tx.amount == order.amount_total and tx.payment_method_code != 'credit'
                for tx in order.transaction_ids
            )

    def action_confirm(self):
        enable_partner_credit_limit_block = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.enable_partner_credit_limit_block", default=False)
        )
        enable_partner_limit_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.enable_partner_limit_key", default=False)
        )

        if enable_partner_credit_limit_block:
            if enable_partner_limit_key:
                self._handle_credit_key()
            else:
                self._validate_credit_limit_block()
        res = super(SaleOrder, self).action_confirm()
        self._handle_credit_suspend()
        return res

    def _handle_credit_key(self):
        for order in self:
            if order.partner_id.customer_credit_key:
                order.partner_id.customer_credit_key = False
            else:
                order._validate_credit_limit_block()

    def _handle_credit_suspend(self):
        for order in self:
            if order.is_paid_via_transaction:
                continue
            if order.partner_id.customer_credit_key:
                continue
            if order.partner_id.customer_manual_suspend:
                continue
            if order.partner_id.total_residual >= order.partner_id.credit_limit:
                order.partner_id.customer_credit_suspend = True

    def _validate_credit_limit_block(self):
        for order in self:
            if order.payment_term_id.payment_term_cash or order.is_paid_via_transaction:
                continue
            if order.partner_credit_warning or order.partner_id.customer_credit_suspend:
                raise ValidationError(
                    "Se ha alcanzado el límite de crédito del cliente o el cliente tiene el credito suspendido. "
                    "Aumente el límite de crédito o desactive esta validación para continuar."
                )

