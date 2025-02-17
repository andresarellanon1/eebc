import logging
from odoo import fields, models
from odoo.tools.float_utils import float_round


logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    landed_cost = fields.Many2one("stock.landed.cost", string="Costos destino")

    # def _get_stock_move_price_unit(self):
    #     """
    #         Honestly, I'm not entirely sure what this code is doing, but here's the deal:
    #
    #         This method overrides the base behavior to handle currency conversion for the
    #         'stock.move' price unit. By default, this price unit is calculated only for
    #         inbound 'stock.move'.
    #
    #         My goal was to ensure all price units are converted from a foreign currency
    #         using the 'landed.cost' custom date's currency rate. However, it seems this price
    #         unit isn't really used anywhere meaningful in the code... but I applied the custom
    #         currency conversion date anyway.
    #
    #         Inshallah, this decision make sense someday. Good luck debugging this.
    #     """
    #     self.ensure_one()
    #     order = self.order_id
    #     price_unit = self.price_unit
    #     price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
    #     if self.taxes_id:
    #         qty = self.product_qty or 1
    #         price_unit = self.taxes_id.with_context(round=False).compute_all(
    #             price_unit, currency=self.order_id.currency_id, quantity=qty, product=self.product_id, partner=self.order_id.partner_id
    #         )['total_void']
    #         price_unit = price_unit / qty
    #     if self.product_uom.id != self.product_id.uom_id.id:
    #         price_unit *= self.product_uom.factor / self.product_id.uom_id.factor
    #     if order.currency_id != order.company_id.currency_id:
    #         convertion_date = self.date_order or fields.Date.today()
    #         if self.landed_cost:
    #             convertion_date = self.landed_cost.date
    #         price_unit = order.currency_id._convert(
    #             price_unit, order.company_id.currency_id, self.company_id, convertion_date, round=False)
    #     return float_round(price_unit, precision_digits=price_unit_prec)
    #
    # def _prepare_account_move_line(self, move=False):
    #     """
    #         Mashallah, it looks like we're using the stock move date to compute
    #         the values for the inbound accounting lines.
    #
    #         This method prepares the accounting move line dictionary with all the necessary
    #         values, including currency conversions, tax computations, and analytic distributions.
    #         It's unclear why the date of the stock move matters here, but it does.
    #         Proceed with caution.
    #     """
    #     self.ensure_one()
    #     aml_currency = move and move.currency_id or self.currency_id
    #     date = move and move.date or fields.Date.today()
    #     price_unit = self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False)
    #     res = {
    #         'display_type': self.display_type or 'product',
    #         'name': '%s: %s' % (self.order_id.name, self.name),
    #         'product_id': self.product_id.id,
    #         'product_uom_id': self.product_uom.id,
    #         'quantity': self.qty_to_invoice,
    #         'discount': self.discount,
    #         'price_unit': price_unit,
    #         'tax_ids': [(6, 0, self.taxes_id.ids)],
    #         'purchase_line_id': self.id,
    #     }
    #     if self.analytic_distribution and not self.display_type:
    #         res['analytic_distribution'] = self.analytic_distribution
    #     return res
