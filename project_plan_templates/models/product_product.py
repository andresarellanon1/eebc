from odoo import fields, models, api

class ProductProduct(models.Model):

    _inherit = 'product.product'

    project_quantity = fields.Integer(string="Cantidad")