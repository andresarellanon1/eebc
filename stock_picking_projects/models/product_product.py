from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    quantity = fields.Integer(string='Cantidad')