from odoo import api, fields, models

import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    locked_currency_rate = fields.Float(
        string="Tipo de cambio",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo a la divisa seleccionada y al tipo de cambio oficial del día.",
    )

    @api.onchange("currency_id")
    def onchange_currency_rate(self):
        for order in self:
            if order.state == "done":
                return
            else:
                locked_currency = self.env["ir.config_parameter"].sudo().get_param("sale.locked_currency")
                order.locked_currency_rate = self.env["res.currency"].search([("id", "=", locked_currency.id)], limit=1).inverse_rate
                order._compute_product_lines()

    def _compute_product_lines(self):
        for order in self:
            for line in order.order_line:
                line._product_id_change()
