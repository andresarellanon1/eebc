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
    """
    Campo Booleano: 'is_paid_via_transaction'
    1. Indica si la orden ha sido pagada a través de una transacción válida.
    2. Se calcula automáticamente con base en el estado, monto y método de pago de las transacciones asociadas.
    3. Se almacena en la base de datos para optimizar consultas posteriores.
    """

    @api.depends('transaction_ids.state', 'transaction_ids.amount', 'amount_total', 'transaction_ids.payment_method_code')
    def _compute_is_paid_via_transaction(self):
        """
        Computa si la orden ha sido pagada mediante una transacción.
        1. Itera sobre las transacciones asociadas a la orden.
        2. Verifica que el estado sea 'done', el monto coincida con el total de la orden,
           y el método de pago no sea crédito.
        3. Si alguna transacción cumple las condiciones, se marca como True.
        """
        for order in self:
            order.is_paid_via_transaction = any(
                tx.state == 'done' and tx.amount == order.amount_total and tx.payment_method_code != 'credit'
                for tx in order.transaction_ids
            )

    def action_confirm(self):
        """
        Sobrescribe el método action_confirm para agregar validaciones relacionadas con el crédito del cliente.
        1. Obtiene las configuraciones para habilitar las validaciones de crédito.
        2. Si la validación está habilitada:
            - Verifica si la llave de crédito está activa (enable_partner_limit_key).
            - Si no está activa, valida el límite de crédito directamente.
        3. Confirma la orden y realiza validaciones adicionales relacionadas con la suspensión de crédito.
        """
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
        """
        Maneja la funcionalidad de la llave de crédito para las órdenes.
        1. Verifica si el cliente tiene una llave de crédito activa.
        2. Si está activa, la desactiva.
        3. Si no está activa, valida el límite de crédito.
        """
        for order in self:
            if order.partner_id.customer_credit_key:
                order.partner_id.customer_credit_key = False
            else:
                order._validate_credit_limit_block()

    def _handle_credit_suspend(self):
        """
        Maneja la suspensión automática de crédito para clientes.
        1. Ignora órdenes pagadas mediante transacciones o clientes con llave de crédito.
        2. Si el total residual del cliente excede el límite de crédito, se suspende automáticamente.
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

    def _validate_credit_limit_block(self):
        """
        Valida si la orden excede el límite de crédito del cliente.
        1. Omite validaciones para órdenes con pago inmediato o pagadas mediante transacciones.
        2. Si el cliente tiene advertencias de crédito o el crédito está suspendido, lanza un error.
        """
        for order in self:
            if order.payment_term_id.payment_term_cash or order.is_paid_via_transaction:
                continue
            if order.partner_credit_warning or order.partner_id.customer_credit_suspend:
                raise ValidationError(
                    "Se ha alcanzado el límite de crédito del cliente o el cliente tiene el crédito suspendido. "
                    "Aumente el límite de crédito o desactive esta validación para continuar."
                )
