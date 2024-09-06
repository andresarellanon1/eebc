from odoo import fields, models, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # location = fields.Many2one('res.company', string="Location", default=lambda self: self.env.user.company_id.id)
