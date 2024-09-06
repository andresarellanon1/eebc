from odoo import fields, models, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    location = fields.Many2one('res.company', string="Location", 
        default=lambda self: self.env.user.company_id.id)

    @api.onchange('company_id')
    def _location_onchange(self):
        if self.company_id:
            return {
                'domain': {
                    'location': [('parent_id', '=', self.company_id.id)]
                }
        }