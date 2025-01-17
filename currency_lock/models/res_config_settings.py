from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    locked_currency_id = fields.Many2one(
        string="Divisa",
        help="Divisa.",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

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
        self.env.user.company_id.locked_currency_id = self.locked_currency_id

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            locked_currency_id=self.env.user.company_id.locked_currency_id.id
        )
        return res
