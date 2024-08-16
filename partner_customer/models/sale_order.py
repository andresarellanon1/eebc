from odoo import _, api, fields, models
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def onchange_partner_invoicing(self):
        for order in self:
            order.partner_invoice_id = order.partner_id
            order.partner_shipping_id = order.partner_id
