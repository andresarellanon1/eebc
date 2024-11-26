from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)

class EEBCConfigurationSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_purchase_location_reference = fields.Boolean(string="Referencia de ubicación en el folio de compras.", default=lambda self: self.env["ir.config_parameter"].get_param("purchase.enable_purchase_location_reference", default=False))

    def set_values(self):
        super(EEBCConfigurationSettings, self).set_values()
        params = self.env["ir.config_parameter"]

        params.set_param("purchase.enable_purchase_location_reference", self.enable_purchase_location_reference)

    def get_values(self):
        res = super(EEBCConfigurationSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()

        res.update({
            "enable_purchase_location_reference": params.get_param("purchase.enable_purchase_location_reference", default=False),
        })

        return res