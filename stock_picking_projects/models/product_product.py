from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    project_id = fields.Many2one('project.project', string='Proyecto')