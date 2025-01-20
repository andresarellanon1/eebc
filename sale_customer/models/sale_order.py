from odoo import _, api, fields, models
import logging

logger = logging.getLogger(__name__)

# TODO: REMOVE USELESS OR ODOO-INSTANCE SPECIFIC CODE, MAKE THIS MODEL AS GENERIC AS POSSIBLE


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_reference = fields.Char(string="Orden de compra", help="Referencia de la orden de compra del cliente. Este campo no representa una orden de compra dentro de odoo. Se refiere a una orden de compra en el sistema del cliente.")

    @api.onchange("partner_id")
    def onchange_partner_invoicing(self):
        for order in self:
            order.partner_invoice_id = order.partner_id
            order.partner_shipping_id = order.partner_id
