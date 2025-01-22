from odoo import api, fields, models
import logging
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    #
    # purchase_price = fields.Float(
    #     string="Costo Unitario",
    #     compute="_compute_purchase_price",
    #     digits='Product Price',
    #     store=True,
    #     readonly=False,
    #     copy=False,
    #     groups="base.group_user")

    # def _get_branch_average_unit_price(self, product_id, demand_qty, qty_invoiced=0):
    #     """
    #     Calculate the average unit price for a product considering branch-specific valuation layers.
    #
    #     :param product_id: The product to calculate the average unit price for.
    #     :param demand_qty: The quantity to process.
    #     :param qty_invoiced: The quantity already invoiced, to exclude from calculations.
    #     :return: The average unit price for the demand quantity.
    #     """
    #     self.ensure_one()
    #
    #     # Early exit if no demand
    #     if not demand_qty:
    #         return 0.0
    #
    #     # Fetch valuation layers for the product and branch, sorted by creation date
    #     valuation_layers = self.env['stock.valuation.layer'].search([
    #         ('product_id', '=', product_id.id),
    #         ('branch_id', '=', self.order_id.branch_id.id),
    #         ('remaining_qty', '>', 0)
    #     ], order='create_date ASC')
    #
    #     if not valuation_layers:
    #         # Fallback to standard price if no valuation layers exist
    #         return product_id.standard_price
    #
    #     total_qty = 0.0
    #     total_cost = 0.0
    #     qty_to_value = demand_qty
    #
    #     # Exclude invoiced quantities by "consuming" layers
    #     for layer in valuation_layers:
    #         if qty_invoiced <= 0:
    #             break
    #         to_consume = min(layer.remaining_qty, qty_invoiced)
    #         qty_invoiced -= to_consume
    #
    #     # Process layers to value the demand quantity
    #     for layer in valuation_layers:
    #         if qty_to_value <= 0:
    #             break
    #
    #         available_qty = min(layer.remaining_qty, qty_to_value)
    #         total_cost += available_qty * layer.unit_cost
    #         total_qty += available_qty
    #         qty_to_value -= available_qty
    #
    #     # If demand exceeds available layers, use the standard price for the missing quantity
    #     if qty_to_value > 0:
    #         total_cost += product_id.standard_price * qty_to_value
    #         total_qty += qty_to_value
    #
    #     # Return the average unit price
    #     return total_cost / demand_qty if demand_qty > 0 else 0.0

    # @api.depends('move_ids', 'move_ids.picking_id.state', 'product_id', 'company_id', 'currency_id', 'product_uom', 'product_uom_qty')
    # def _compute_purchase_price(self):
    #     lines_without_moves = self.browse()
    #     for line in self:
    #         product = line.product_id.with_company(line.company_id)
    #
    #         # Only god knows why this is here... commented out the block
    #         if not line.has_valued_move_ids():
    #             lines_without_moves |= line
    #         # if product and product.categ_id.property_cost_method == 'averange':
    #         purch_price = product._compute_average_price(line.qty_invoiced, line.product_uom_qty, line.move_ids)
    #         if line.product_uom and line.product_uom != product.uom_id:
    #             purch_price = product.uom_id._compute_price(purch_price, line.product_uom)
    #         line.purchase_price = line._convert_to_sol_currency(
    #             purch_price,
    #             product.cost_currency_id,
    #         )
    #     return super(SaleOrderLine, lines_without_moves)._compute_purchase_price()
    # elif product and product.categ_id.property_cost_method == 'fifo':
    # there is no fifo, it's always average_cost
    # purch_price = line._get_branch_average_unit_price(product, line.product_uom_qty, line.qty_invoiced)
    # if line.product_uom and line.product_uom != product.uom_id:
    #     purch_price = product.uom_id._compute_price(purch_price, line.product_uom)
    # line.purchase_price = line._convert_to_sol_currency(
    #     purch_price,
    #     product.cost_currency_id,
    # )
# === Just for reading and studying purposes we keep this 2 blocks commented === #
    # NOTE: never used, just for concept of RAW average cost
    # def calculate_average_cost(self):
    #     existing_layers = self.env['stock.valuation.layer'].search([('quantity', '>', 0)])
    #
    #     total_cost = sum(layer.unit_cost * layer.quantity for layer in existing_layers)
    #     total_units = sum(layer.quantity for layer in existing_layers)
    #
    #     if total_units == 0:
    #         return 0
    #
    #     weighted_average_cost = total_cost / total_units
    #
    #     return weighted_average_cost
    # NOTE: original computation for purchase price
    # @api.depends('move_ids', 'move_ids.stock_valuation_layer_ids', 'move_ids.picking_id.state')
    # def _compute_purchase_price(self):
    #     lines_without_moves = self.browse()
    #     for line in self:
    #         product = line.product_id.with_company(line.company_id)
    #         # This 2 lines does not make sense tu me, may comment them out later after testing ...
    #         if not line.has_valued_move_ids():
    #             lines_without_moves |= line
    #         elif product and product.categ_id.property_cost_method != 'standard':
    #             purch_price = product._compute_average_price(0, line.product_uom_qty, line.move_ids)
    #             if line.product_uom and line.product_uom != product.uom_id:
    #                 purch_price = product.uom_id._compute_price(purch_price, line.product_uom)
    #             # to_cur = line.currency_id or line.order_id.currency_id
    #             line.purchase_price = line._convert_to_sol_currency(
    #                 purch_price,
    #                 product.cost_currency_id,
    #             )
    #     # DEVELOPER NOTE:
    #     # IDK WHY WOULD WE CALL THE BASE METHOD AFTER COMPUTING THE VALUE,
    #     # THIS JUST MAKES THE VALUE GET COMPUTED AGAIN BUT IGNORING EVERYTHING WE JUST DID RIGHT ABOUVE THIS LINE ??????
    #     # Just comment the line out
    #     return super(SaleOrderLine, lines_without_moves)._compute_purchase_price()
