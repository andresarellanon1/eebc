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

    target_currency_id = fields.Many2one(
        string="Divisa Objetivo",
        comodel_name="res.currency",
        default=lambda self: self.env.company.locked_currency_id.id,
    )

    @api.depends("pricelist_id", "company_id")
    def _compute_currency_id(self):
        """
        NOTE: This override prevents currency from being computed on previously loaded modules
        WARNING: This is critical to allow the target_currency_id to be transfered to the currency_id of the 'sale.order' document
        """
        for order in self:
            order.currency_id = order.target_currency_id

    @api.onchange("target_currency_id")
    def onchange_currency_rate(self):
        for order in self:
            if order.state == "sale":
                return

            order.currency_id = order.target_currency_id
            order.locked_currency_rate = order.target_currency_id.inverse_rate + order.safe_margin
            order._compute_pricelist_prices()

    @api.onchange("partner_id")
    def onchange_customer_partner_id(self):
        for order in self:
            order.target_currency_id = order.partner_id.sales_currency_id
            order.currency_id = order.target_currency_id
            target_currency = order.target_currency_id if order.target_currency_id else self.env.company.currency_id
            order.locked_currency_rate = target_currency.inverse_rate + order.safe_margin
            order._compute_pricelist_prices()

    def _compute_pricelist_prices(self):
        """
        Override to implement custom pricelist computing
        e.g.
        for line in order.order_line:
                line._compute_pricelist_price_unit()
        """
        return
