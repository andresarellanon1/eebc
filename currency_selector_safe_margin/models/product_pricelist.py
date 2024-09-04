from odoo import fields, models, api

class ProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    company_id = fields.Many2one(default = lambda self: self.env['company_id.id'])