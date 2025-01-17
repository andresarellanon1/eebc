from odoo import fields, models, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    location_id = fields.Many2one('res.company', string="Location")
