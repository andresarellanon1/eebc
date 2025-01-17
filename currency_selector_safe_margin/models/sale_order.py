import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    locked_currency_rate = fields.Float(
        string="Tipo de cambio seguro",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo al tipo de cambio oficial del día en curso. Una vez confirmado el documento no se ‘bloquea’ permanentemente o hasta que se devuelva el documento a borrador.",
    )

    safe_margin = fields.Float(
        string="Margen seguro",
        digits="Product Price",
        help="Agrega el equivalente a esta cantidad de pesos por cada dólar convertido. Para efectos prácticos esto es como tomar el tipo de cambio del día y sumarle esta cantidad.",
        compute='_compute_safe_margin',
    )

    locked_currency_id = fields.Many2one(
        string="Divisa",
        help="Divisa bloqueada.",
        comodel_name="res.currency",
        default=lambda self: self.env.company.locked_currency_id.id,
    )

    def _compute_safe_margin(self):
        for order in self:
            order.safe_margin = self.env["ir.config_parameter"].sudo().get_param("sale.safe_margin")

    @api.depends("pricelist_id", "company_id")
    def _compute_currency_id(self):
        """
        NOTE: This override prevents currency from being computed on previously loaded modules
        WARNING: This is critical to allow the locked_currency_id to be transfered to the currency_id of the 'sale.order' document
        """
        for order in self:
            order.currency_id = order.locked_currency_id

    @api.onchange("safe_margin")
    def onchange_safe_margin(self):
        for order in self:
            # REPEATED CODE 3 TIMES, MIGHT AS WELL MAKE A METHOD, no lo hago porque no tengo tiempo ni ganas, copy paste
            target_currency = order.locked_currency_id if order.locked_currency_id else self.env.company.currency_id
            order.locked_currency_rate = target_currency.inverse_rate + order.safe_margin
            for line in order.order_line:
                line._compute_pricelist_price_unit()

    @api.onchange("locked_currency_id")
    def onchange_currency_rate(self):
        for order in self:
            if order.state == "sale":
                return

            order.currency_id = order.locked_currency_id
            # REPEATED CODE 3 TIMES, MIGHT AS WELL MAKE A METHOD, no lo hago porque no tengo tiempo ni ganas, copy paste
            order.locked_currency_rate = order.locked_currency_id.inverse_rate + order.safe_margin
            for line in order.order_line:
                line._compute_pricelist_price_unit()

    @api.onchange("partner_id")
    def onchange_customer_partner_id(self):
        for order in self:
            order.locked_currency_id = order.partner_id.sales_currency_id
            order.currency_id = order.locked_currency_id
            # REPEATED CODE 3 TIMES, MIGHT AS WELL MAKE A METHOD, no lo hago porque no tengo tiempo ni ganas, copy paste
            target_currency = order.locked_currency_id if order.locked_currency_id else self.env.company.currency_id
            order.locked_currency_rate = target_currency.inverse_rate + order.safe_margin
            for line in order.order_line:
                line._compute_pricelist_price_unit()
