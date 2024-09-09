from odoo import fields, models, api

class Company(models.Model):
    _inherit = "res.company"

    default_product_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Default Product Pricelist',
        help="This pricelist will be used as the default system-wide.",
        store=True
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_product_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Default Product Pricelist',
        default_model = 'res.config.settings',
        default=lambda self: self.env['product.pricelist'].browse(1),
        related='company.default_product_pricelist_id',
        readonly=False,
        help="This pricelist will be used as the default system-wide."
    )

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.user.company_id.default_product_pricelist_id = self.default_product_pricelist_id

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            default_product_pricelist_id=self.env.company.default_product_pricelist_id.id
        )
        return res