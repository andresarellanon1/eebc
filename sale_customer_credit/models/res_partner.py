from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    orders_residual = fields.Monetary(string='Ordenes por facturar', compute='orders_amount_residual')
    invoice_residual = fields.Monetary(string='Facturas por cobrar', compute='invoice_residual_amount')
    total_residual = fields.Monetary(string='Total por cobrar', compute='_compute_total')
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
        for record in self:
            credit = record.credit + amount
            if not record.customer_manual_suspend and (credit >= record.credit_limit):
                return True
            else:
                return False

    def invoice_residual_amount(self):
        for partner in self:
            credit = partner.credit
            partner.invoice_residual = credit

    @api.depends("orders_residual", "invoice_residual")
    def _compute_total(self):
        for record in self:
            record.total_residual = record.orders_residual + record.invoice_residual

    def orders_amount_residual(self):
        for partner in self:
            total = 0.0
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),  # cliente
                ('state', '=', 'sale'),  # ordenes confirmadas
                ('invoice_status', '=', 'to invoice')  # por facturar
            ])
            for order in orders:
                total += order.amount_total
            partner.orders_residual = total
