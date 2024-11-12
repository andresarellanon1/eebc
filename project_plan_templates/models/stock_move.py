from odoo import fields, models, api

class StockMove(models.Model):

    _inherit = 'stock.move'

    product_ids = fields.Many2many('product.product', string="Productos")