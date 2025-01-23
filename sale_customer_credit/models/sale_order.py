from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError


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
            # Determine if the sale order is paid via a valid transaction
            # Exclude transactions with the 'credit' method; this transactions are not paid by nature.
            order.is_paid_via_transaction = any(
                tx.state == 'done' and tx.amount == order.amount_total and tx.payment_method_code != 'credit'
                for tx in order.transaction_ids
            )

    def action_confirm(self):
        enable_partner_credit_limit_block = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.enable_partner_credit_limit_block")
        )
        enable_partner_limit_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.enable_partner_limit_key")
        )

        if enable_partner_credit_limit_block:
            if enable_partner_limit_key:
                self._handle_credit_key()
            else:
                self._validate_credit_limit_block()
        res = super(SaleOrder, self).action_confirm()
        self._handle_credit_suspend()
        return res

    # Handlers
    def _handle_credit_key(self):
        """
        If Credit key usage is available, turn it off and do no futher validation for the credit limit. Single usage activation behavior.
        Otherwise just check the credit block.
        """
        for order in self:
            if order.partner_id.customer_credit_key:
                order.partner_id.customer_credit_key = False
            else:
                order._validate_credit_limit_block()

    def _handle_credit_suspend(self):
        """
        Suspends the credit if 'credit key' is not enabled and automatic control is available.
        Called after the actual confirmation of the sale order.
        Do not stop the workflow, suspends the credit AFTER the sale order that will overpass the limit is confirmed.
        This will happend regardless of the payment terms, origin or transaction status: always suspend the credit when the limit is rebased anyhow.
        Only the credit key can save the customer from getting his credit suspended.
        """
        for order in self:
            if order.is_paid_via_transaction:
                continue
            if order.partner_id.customer_credit_key:
                continue
            if order.partner_id.customer_manual_suspend:
                continue
            if order.partner_id.total_residual >= order.partner_id.credit_limit:
                order.partner_id.customer_credit_suspend = True

    # Credit Validations
    def _validate_credit_limit_block(self):
        """
        If the payment term is cash or the order has paid transacions that fulfill the order amount, continue with workflow.
        Otherwise, check if credit warning is being shown or if the credit is suspended.
        """
        for order in self:
            if order.payment_term_id.payment_term_cash or order.is_paid_via_transaction:
                continue
            if order.partner_credit_warning or order.partner_id.customer_credit_suspend:
                raise ValidationError(
                    "Se ha alcanzado el límite de crédito del cliente o el cliente tiene el credito suspendido. "
                    "Aumente el límite de crédito o desactive esta validación para continuar."
                )
