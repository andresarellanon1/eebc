from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    orders_residual = fields.Monetary(string='Ordenes por facturar', compute='_compute_orders_residual')
    invoice_residual = fields.Monetary(string='Facturas por cobrar', compute='_compute_invoice_residual')
    total_residual = fields.Monetary(string='Total por cobrar', compute='_compute_total_residual')
    customer_credit_suspend = fields.Boolean(
        default=False,
        string="Crédito suspendido.",
    )
    customer_manual_suspend = fields.Boolean(
        default=False,
        string="Crédito suspendido manual"
    )
    customer_credit_key = fields.Boolean(
        default=False,
        string="Llave de crédito.",
        help="Abrir la llave de crédito.")

    def _check_credit_limit(self, amount):
        for partner in self:
            credit = partner.total_residual + amount
            return (not partner.customer_manual_suspend) and (credit <= partner.credit_limit)

    def _compute_invoice_residual(self):
        for partner in self:
            partner.invoice_residual = partner.credit

    @api.depends("orders_residual", "invoice_residual")
    def _compute_total_residual(self):
        for record in self:
            record.total_residual = record.orders_residual + record.invoice_residual

    def _compute_orders_residual(self):
        for partner in self:
            total = 0.0
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'sale'),  # ordenes confirmadas
                ('invoice_status', '=', 'to invoice')  # por facturar
            ])
            for order in orders:
                total += order.amount_total
            partner.orders_residual = total
