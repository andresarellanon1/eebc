from odoo import api, fields, models
import logging

logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    available_product_quantity = fields.Float(
        compute='_compute_available_product_quantity',
        string='Cantidad disponible en inventario de almacen SUM sin reservar',
        store=True
    )

    @api.depends('product_id', 'order_id.warehouse_id')
    def _compute_available_product_quantity(self):
        for line in self:
            stock_location_wh = line.order_id.warehouse_id.lot_stock_id
            location = self.env['stock.location'].search([('id', '=', stock_location_wh.id)], limit=1)

            logger.warning(f"locacion: {location.name}")

            if not location:
                # Si no existe la ubicación, establece la cantidad disponible como 0
                line.available_product_quantity = 0
                return

            if not line.product_id:
                # Si no hay producto, establece la cantidad disponible como 0
                line.available_product_quantity = 0
                continue

            # Busca los quants del producto en la ubicación especificada
            quants = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', 'child_of', location.id),
                ('location_id.usage', '=', 'internal'),
                ('company_id', '=', line.company_id.id) 
            ])

            # Suma las cantidades disponibles y restadas las reservadas
            total_quantity = sum(quants.mapped('quantity'))
            reserved_quantity = sum(quants.mapped('reserved_quantity'))
            line.available_product_quantity = total_quantity - reserved_quantity
