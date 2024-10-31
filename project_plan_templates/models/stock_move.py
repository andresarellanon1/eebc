from odoo import fields, models, api

class StockMove(models.Model):
   
    _inherit = 'stock.move'

    product_ids = fields.One2many('project.picking.lines', 'stock_move_id', string='stock product')
    product_id = fields.Many2one('product.product', string='product', domain="[('id', 'in', 'product_ids.mapped('product_id').ids')]")
    