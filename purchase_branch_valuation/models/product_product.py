from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_repr, float_round, float_compare
from odoo.exceptions import ValidationError
from collections import defaultdict


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # TODO: add branch checking for average???
    # def _compute_average_price(self, qty_invoiced, qty_to_invoice, stock_moves, is_returned=False):
    #     """Go over the valuation layers of `stock_moves` to value `qty_to_invoice` while taking
    #     care of ignoring `qty_invoiced`. If `qty_to_invoice` is greater than what's possible to
    #     value with the valuation layers, use the product's standard price.
    #
    #     :param qty_invoiced: quantity already invoiced
    #     :param qty_to_invoice: quantity to invoice
    #     :param stock_moves: recordset of `stock.move`
    #     :param is_returned: if True, consider the incoming moves
    #     :returns: the anglo saxon price unit
    #     :rtype: float
    #     """
    #     self.ensure_one()
    #     if not qty_to_invoice:
    #         return 0
    #     candidates = stock_moves\
    #         .sudo()\
    #         .filtered(lambda m: is_returned == bool(m.origin_returned_move_id and sum(m.stock_valuation_layer_ids.mapped('quantity')) >= 0))\
    #         .mapped('stock_valuation_layer_ids')\
    #         .sorted()
    #     value_invoiced = self.env.context.get('value_invoiced', 0)
    #     if 'value_invoiced' in self.env.context:
    #         qty_valued, valuation = candidates._consume_all(qty_invoiced, value_invoiced, qty_to_invoice)
    #     else:
    #         qty_valued, valuation = candidates._consume_specific_qty(qty_invoiced, qty_to_invoice)
    #     # If there's still quantity to invoice but we're out of candidates, we chose the standard
    #     # price to estimate the anglo saxon price unit.
    #     missing = qty_to_invoice - qty_valued
    #     for sml in stock_moves.move_line_ids:
    #         if not sml._should_exclude_for_valuation():
    #             continue
    #         missing -= sml.product_uom_id._compute_quantity(sml.quantity, self.uom_id, rounding_method='HALF-UP')
    #     if float_compare(missing, 0, precision_rounding=self.uom_id.rounding) > 0:
    #         valuation += self.standard_price * missing
    #     return valuation / qty_to_invoice
