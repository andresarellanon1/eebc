import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """
    This model extends the functionality of `sale.order` to add features for handling target currencies, safe margins,
    and locked exchange rates. It provides methods to compute and manage these custom fields and overrides standard
    behaviors to integrate seamlessly with Odoo's sales order workflow.
    """
    _inherit = "sale.order"

    target_currency_id = fields.Many2one(
        string="Divisa Objetivo",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id
    )

    locked_currency_rate = fields.Float(
        string="Tipo de cambio seguro",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo al tipo de cambio oficial del día en curso. Una vez confirmado el documento; se ‘bloquea’ permanentemente o hasta que se devuelva el documento a borrador.",
        compute="_compute_locked_currency_rate",
        default=lambda self: self.env.company.currency_id.inverse_rate,
        readonly=False,
        store=True
    )

    safe_margin = fields.Float(
        string="Margen seguro",
        digits="Product Price",
        help="Agrega el equivalente a esta cantidad de pesos por cada dólar convertido. Para efectos prácticos esto es como tomar el tipo de cambio del día y sumarle esta cantidad.",
        compute='_compute_safe_margin',
        store=True,
        readonly=False,
    )

    @api.depends("company_id", "company_id.safe_margin")
    def _compute_safe_margin(self):
        """
            Computes the safe margin value for the sale order based on the company's safe margin configuration.
        """
        for order in self:
            order.safe_margin = order.company_id.safe_margin

    @api.depends("safe_margin", "target_currency_id", "target_currency_id.inverse_rate")
    def _compute_locked_currency_rate(self):
        """
            Set the locked currency rate using the inverse rate of the target currency, adjusted by the new safe margin.
        """
        for order in self:
            if order.state == "sale":
                order.locked_currency_rate = order.locked_currency_rate
            else:
                order.locked_currency_rate = order.target_currency_id.inverse_rate + order.safe_margin

    @api.depends("pricelist_id", "company_id", "target_currency_id")
    def _compute_currency_id(self):
        """
            Overrides the computation of the `currency_id` field to ensure it is derived from the `target_currency_id`.
            Prevents recalculation of the currency for pre-existing records, enabling the smooth transfer of
            the target currency to the sale order's currency.
        """
        for order in self:
            order.currency_id = order.target_currency_id

    @api.onchange("partner_id")
    def _onchange_parnter(self):
        """
            Unless the sale order is already confirmed.
            Updates the field `target_currency_id` when the customer (`partner_id`) is changed.
            Sets the target currency to the customer's sales currency and
            recomputes the exchange rate and prices.
            Updates the pricelist prices for the whole sale order.
        """
        for order in self:
            if order.state == "sale":
                continue
            order.target_currency_id = order.partner_id.sales_currency_id
            order._compute_pricelist_prices()

    @api.onchange("target_currency_id")
    def _onchange_locked_currency(self):
        """
            Binds the currency id to match the target target currency id.
            Updates the pricelist prices for the whole sale order.
        """
        for order in self:
            logger.warning("== > == < ==")
            if order.state == "sale":
                continue
            order.currency_id = order.target_currency_id
            order._compute_pricelist_prices()

    def _compute_pricelist_prices(self):
        """
            Placeholder method for custom logic to compute prices based on the selected pricelist. Intended to recalculate
            prices for order lines dynamically. This method should be overridden in specific implementations as needed.
            This module should be shipped witha lil-brother-module to perform custom price unit calculation using a pricelist or a custom algorithm.
        """
        return
