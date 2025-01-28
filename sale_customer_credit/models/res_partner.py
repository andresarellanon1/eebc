from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extiende el modelo res.partner para agregar campos y métodos relacionados con la gestión de crédito."""

    _inherit = "res.partner"

    orders_residual = fields.Monetary(string='Ordenes por facturar', compute='_compute_orders_residual')
    invoice_residual = fields.Monetary(string='Facturas por cobrar', compute='_compute_invoice_residual')
    total_residual = fields.Monetary(string='Total por cobrar', compute='_compute_total_residual')
    customer_credit_suspend = fields.Boolean(default=False, string="Crédito suspendido.")
    customer_manual_suspend = fields.Boolean(default=False, string="Crédito suspendido manual")
    customer_credit_key = fields.Boolean(default=False, string="Llave de crédito.", help="Abrir la llave de crédito.")

    def _check_credit_limit(self, amount):
        """Verifica si se ha alcanzado el límite de crédito del partner.

        Flujo:
        1. Suma el monto ingresado al crédito total del partner.
        2. Verifica si el crédito total excede el límite definido.
        3. Retorna True si el límite no se excede y no está suspendido manualmente.

        Args:
            amount (float): El monto que se agregará al crédito del partner.

        Returns:
            bool: True si no se ha alcanzado el límite de crédito, False en caso contrario.
        """
        for partner in self:
            credit = partner.total_residual + amount
            return (not partner.customer_manual_suspend) and (credit <= partner.credit_limit)

    def _compute_invoice_residual(self):
        """Calcula el monto residual de las facturas para el partner.

        Flujo:
        1. Obtiene el monto actual de crédito del partner.
        2. Asigna este valor al campo `invoice_residual`.
        """
        for partner in self:
            partner.invoice_residual = partner.credit

    @api.depends("orders_residual", "invoice_residual")
    def _compute_total_residual(self):
        """Calcula el monto residual total (órdenes + facturas) para el partner.

        Flujo:
        1. Suma los valores de `orders_residual` y `invoice_residual`.
        2. Asigna este total al campo `total_residual`.
        """
        for record in self:
            record.total_residual = record.orders_residual + record.invoice_residual

    def _compute_orders_residual(self):
        """Calcula el monto residual de las órdenes para el partner.

        Flujo:
        1. Busca todas las órdenes confirmadas y por facturar del partner.
        2. Suma el monto total de estas órdenes.
        3. Asigna este total al campo `orders_residual`.
        """
        for partner in self:
            total = 0.0
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'sale'),  # órdenes confirmadas
                ('invoice_status', '=', 'to invoice')  # por facturar
            ])
            for order in orders:
                total += order.amount_total
            partner.orders_residual = total
