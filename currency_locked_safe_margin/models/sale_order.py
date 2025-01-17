import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    safe_margin = fields.Float(
        string="Margen seguro",
        digits="Product Price",
        help="Agrega el equivalente a esta cantidad de pesos por cada dólar convertido. Para efectos prácticos esto es como tomar el tipo de cambio del día y sumarle esta cantidad.",
        compute='_compute_safe_margin',
    )

    def _compute_safe_margin(self):
        for order in self:
            order.safe_margin = self.env["ir.config_parameter"].sudo().get_param("sale.safe_margin")

    @api.onchange("safe_margin")
    def onchange_safe_margin(self):
        for order in self:
            target_currency = order.target_currency_id if order.target_currency_id else self.env.company.currency_id
            order.locked_currency_rate = target_currency.inverse_rate + order.safe_margin
            for line in order.order_line:
                line._compute_pricelist_price_unit()
