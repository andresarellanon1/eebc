from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo import models, api, fields
import logging
from datetime import date
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_price = fields.Float(
        string="Costo Unitario",
        compute="_compute_purchase_price",
        digits='Product Price',
        store=True,
        readonly=False,
        copy=False,
        groups="base.group_user")

    def _get_fifo_unit_price(self, product_id, demand_qty):
        valuation_layers = self.env['stock.valuation.layer'].search(
            [('product_id', '=', product_id.id)],
            [('branch_id', '=', self.branch_id.id)],
            order='create_date'
        )

        if not valuation_layers:
            return 0  # Devuelve 0 si no hay capas de valoración disponibles

        total_qty = 0
        total_cost = 0

        for layer in valuation_layers:
            if layer.remaining_qty <= 0:
                continue

            if total_qty + layer.remaining_qty >= demand_qty:
                total_cost += (demand_qty - total_qty) * layer.unit_cost
                total_qty = demand_qty
                break
            else:
                total_cost += layer.remaining_qty * layer.unit_cost
                total_qty += layer.remaining_qty

        if total_qty < demand_qty:
            # Ajuste: retornar el costo promedio de lo que se ha acumulado
            return total_cost / total_qty if total_qty > 0 else 0

        average_cost = total_cost / demand_qty
        logger.warning(f"averange cost: {average_cost}")
        return average_cost

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

    @api.depends('move_ids', 'move_ids.picking_id.state', 'product_id', 'company_id', 'currency_id', 'product_uom', 'product_uom_qty')
    def _compute_purchase_price(self):
        for line in self:
            product = line.product_id.with_company(line.company_id)

            # Only god knows why this is here... commented out the block
            # if not line.has_valued_move_ids():
            #     logger.warning(" > > if not line.has_valued_move_ids < < ")
            #     lines_without_moves |= line

            if product and product.categ_id.property_cost_method == 'averange':
                purch_price = product._compute_average_price(0, line.product_uom_qty, line.move_ids)

                if line.product_uom and line.product_uom != product.uom_id:
                    purch_price = product.uom_id._compute_price(purch_price, line.product_uom)

                line.purchase_price = line._convert_to_sol_currency(
                    purch_price,
                    product.cost_currency_id,
                )

                logger.warning(f" > > AVG: {line.purchase_price} < < ")

            elif product and product.categ_id.property_cost_method == 'fifo':
                purch_price = self._get_fifo_unit_price(product, line.product_uom_qty)

                if line.product_uom and line.product_uom != product.uom_id:
                    purch_price = product.uom_id._compute_price(purch_price, line.product_uom)

                line.purchase_price = line._convert_to_sol_currency(
                    purch_price,
                    product.cost_currency_id,
                )
                logger.warning(f" > > FIFO: {line.purchase_price} < < ")

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
    #     # THIS JUST MAKES THE VALUE GET COMPUTED AGAIN BUT IGNORING EVERYTHING WE JUST DID RIGHT ABOUVE THIS LINE lol
    #     # Just comment the line out
    #     return super(SaleOrderLine, lines_without_moves)._compute_purchase_price()
