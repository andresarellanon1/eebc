from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    default_product_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Default Product Pricelist',
        help="This pricelist will be used as the default system-wide.",
        store=True
    )

    locked_currency_id = fields.Many2one(
        string="Divisa",
        help="Divisa.",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_product_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Default Product Pricelist',
        default_model='res.config.settings',
        default=lambda self: self.env['product.pricelist'].browse(1),
        related='company_id.default_product_pricelist_id',
        readonly=False,
        help="This pricelist will be used as the default system-wide."
    )

    locked_currency_id = fields.Many2one(
        'res.currency',
        string='Default Locked Currency',
        default_model='res.config.settings',
        default=lambda self: self.env.company.locked_currency_id.id,
        related='company_id.locked_currency_id',
        readonly=False,
        help="This currency will be used to compute rates and be compatible with the pricelist per line unit price calculations on sale orders."
    )

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.user.company_id.default_product_pricelist_id = self.default_product_pricelist_id
        self.env.user.company_id.locked_currency_id = self.locked_currency_id

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            default_product_pricelist_id=self.env.user.company_id.default_product_pricelist_id.id,
            locked_currency_id=self.env.user.company_id.locked_currency_id.id
        )
        return res
