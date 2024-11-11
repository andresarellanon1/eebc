from odoo import fields, models, api

class StockMove(models.Model):

    _inherit = 'stock.move'

    product_ids = fields.Many2many('product.product', string='Productos')

    product_uom = fields.Many2one(
        'uom.uom', string="Unidad", domain="[('category_id', '=', product_uom_category_id)]")