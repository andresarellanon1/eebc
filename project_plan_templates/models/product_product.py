from odoo import fields, models, api

class ProductProduct(models.Model):

    _inherit = 'product.product'

    project_quantity = fields.Integer(string="Cantidad en el proyecto")
    is_extra = fields.Boolean(string="Material extra", defaut=False)