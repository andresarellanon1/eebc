import logging

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round

logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    # price_unit = fields.Float('Unit Price', copy=False, digits='Product Price')

    # def _get_price_unit(self):
    #     """
    #         It's me again, check the 'purchase.order' method overwritten in this same module called '_get_stock_move_price_unit()'
    #         for more details on why this comment is actually hilarious.
    #         Anyways, this time we compute the price unit of the stock move again but this time it is actually related to something meaningfull (the 'stock.valuation.layer').
    #     """
    #     self.ensure_one()
    #
    #     if self._should_ignore_pol_price():
    #         return super(StockMove, self)._get_price_unit()
    #
    #     price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
    #     line = self.purchase_line_id
    #     order = line.order_id
    #     received_qty = line.qty_received
    #
    #     if self.state == 'done':
    #         received_qty -= self.product_uom._compute_quantity(self.quantity, line.product_uom, rounding_method='HALF-UP')
    #
    #     if line.product_id.purchase_method == 'purchase' and float_compare(line.qty_invoiced, received_qty, precision_rounding=line.product_uom.rounding) > 0:
    #         raise UserError('No está implementado el flujo para control sobre cantidades pedidas.')
    #         move_layer = line.move_ids.sudo().stock_valuation_layer_ids
    #         invoiced_layer = line.sudo().invoice_lines.stock_valuation_layer_ids
    #         # value on valuation layer is in company's currency, while value on invoice line is in order's currency
    #         receipt_value = 0
    #
    #         if move_layer:
    #             receipt_value += sum(move_layer.mapped(lambda l: l.currency_id._convert(
    #                 l.value, order.currency_id, order.company_id, line.landed_cost.date if line.landed_cost else l.create_date, round=False)))
    #
    #         if invoiced_layer:
    #             receipt_value += sum(invoiced_layer.mapped(lambda l: l.currency_id._convert(
    #                 l.value, order.currency_id, order.company_id, line.landed_cost.date if line.landed_cost else l.create_date, round=False)))
    #
    #         invoiced_value = 0
    #         invoiced_qty = 0
    #
    #         for invoice_line in line.sudo().invoice_lines:
    #             if invoice_line.move_id.state != 'posted':
    #                 continue
    #
    #             if invoice_line.tax_ids:
    #                 invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
    #                     invoice_line.price_unit, currency=invoice_line.currency_id, quantity=invoice_line.quantity)['total_void']
    #             else:
    #                 invoiced_value += invoice_line.price_unit * invoice_line.quantity
    #             invoiced_qty += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_id.uom_id)
    #
    #         # TODO: Check if currency conversion will be needed before doing this kinda operations, or maybe not, what the h do i know
    #         remaining_value = invoiced_value - receipt_value
    #         # Do we know what uom_id qty_received is in? is it the base or a custom one?
    #         # Will it matter or not? what will happend if a valid user-input uom made it to this point?
    #         # BTW why is the stock move calculating the average price for? does that even makes sense?
    #         remaining_qty = invoiced_qty - line.product_uom._compute_quantity(received_qty, line.product_id.uom_id)
    #         price_unit = float_round(remaining_value / remaining_qty, precision_digits=price_unit_prec) if remaining_value and remaining_qty else line._get_gross_price_unit()
    #     else:
    #         price_unit = line._get_gross_price_unit()
    #
    #     if order.currency_id != order.company_id.currency_id:
    #         # NOTE: Legacy comment, we don't care, let's call the conversion date of the landing cost lmao
    #
    #         # The date must be today, and not the date of the move since the move move is still
    #         # in assigned state. However, the move date is the scheduled date until move is
    #         # done, then date of actual move processing. See:
    #         # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
    #
    #         # price_unit = order.currency_id._convert(
    #         #     price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
    #
    #         convertion_date = fields.Date.context_today(self)
    #
    #         if line.landed_cost:
    #             convertion_date = line.landed_cost.date
    #
    #         price_unit = order.currency_id._convert(
    #             price_unit, order.company_id.currency_id, order.company_id, convertion_date, round=False)
    #
    # return price_unit
