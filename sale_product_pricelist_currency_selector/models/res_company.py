from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    product_pricelist_id = fields.Many2one('product.pricelist',
                                           string='Default Product Pricelist',
                                           help="This pricelist will be used as the default system-wide.",
                                           default=lambda self: self.env['product.pricelist'].browse(1)
                                           )
