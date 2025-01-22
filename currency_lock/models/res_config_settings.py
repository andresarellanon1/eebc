from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    safe_margin = fields.Float(
        string="Margen seguro",
        digits="Product Price",
        readonly=False,
        help="Agrega el equivalente a esta cantidad de pesos por cada dólar convertido. Para efectos prácticos esto es como tomar el tipo de cambio del día y sumarle esta cantidad.",
        default=0.00,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    safe_margin = fields.Float(
        string="Margen seguro",
        digits="Product Price",
        default_model='res.config.settings',
        readonly=False,
        default=0,
        related='company_id.safe_margin',
        help="Agrega el equivalente a esta cantidad de pesos por cada dólar convertido. Para efectos prácticos esto es como tomar el tipo de cambio del día y sumarle esta cantidad."
    )

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.user.company_id.safe_margin = self.safe_margin

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            safe_margin=self.env.user.company_id.safe_margin
        )
        return res
