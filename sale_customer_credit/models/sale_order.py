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
        """Calcula si la orden de venta ha sido pagada mediante una transacción válida."""
        for order in self:
            order.is_paid_via_transaction = any(
                tx.state == 'done' and tx.amount == order.amount_total and tx.payment_method_code != 'credit'
                for tx in order.transaction_ids
            )

    def action_confirm(self):
        """Valida el límite de crédito del cliente antes de confirmar la orden de venta."""
        enable_partner_credit_limit_block = self.env["ir.config_parameter"].sudo().get_param("sale.enable_partner_credit_limit_block")
        enable_partner_limit_key = self.env["ir.config_parameter"].sudo().get_param("sale.enable_partner_limit_key")

        if enable_partner_credit_limit_block:
            if enable_partner_limit_key:
                self._handle_credit_key()
            else:
                self._validate_credit_limit_block()
        res = super(SaleOrder, self).action_confirm()
        self._handle_credit_suspend()
        return res

    def _handle_credit_key(self):
        """Maneja el uso de la llave de crédito para evitar la validación del límite de crédito."""
        for order in self:
            if order.partner_id.customer_credit_key:
                order.partner_id.customer_credit_key = False
            else:
                order._validate_credit_limit_block()

    def _handle_credit_suspend(self):
        """Suspende el crédito del cliente si se excede el límite."""
        for order in self:
            if not (order.is_paid_via_transaction or order.partner_id.customer_credit_key or order.partner_id.customer_manual_suspend):
                if order.partner_id.total_residual >= order.partner_id.credit_limit:
                    order.partner_id.customer_credit_suspend = True

    def _validate_credit_limit_block(self):
        """Valida si el cliente ha excedido su límite de crédito."""
        for order in self:
            if not (order.payment_term_id.payment_term_cash or order.is_paid_via_transaction):
                if order.partner_credit_warning or order.partner_id.customer_credit_suspend:
                    raise ValidationError(
                        "Se ha alcanzado el límite de crédito del cliente o el cliente tiene el credito suspendido. "
                        "Aumente el límite de crédito o desactive esta validación para continuar."
                    )