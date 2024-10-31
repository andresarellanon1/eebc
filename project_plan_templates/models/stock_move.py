from odoo import fields, models, api

class StockMove(models.Model):
   
    _inherit = 'stock.move'

    product_ids = fields.One2many('project.picking.lines', 'stock_move_id', string='stock product')

    