
from odoo import fields, models
import logging
logger = logging.getLogger(__name__)


class ConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_partner_credit_limit_block = fields.Boolean(string="Bloquear ventas a clientes por límite de crédito excedido.")
    enable_partner_limit_key = fields.Boolean(string="Permite el uso de la llave de crédito para confirmar cotizaciones que sobrepasan el límite de crédito del cliente.")

    def set_values(self):
        super(ConfigSettings, self).set_values()
        params = self.env["ir.config_parameter"]
        params.set_param("sale.enable_partner_credit_limit_block", self.enable_partner_credit_limit_block)
        params.set_param("sale.enable_partner_limit_key", self.enable_partner_limit_key)

    def get_values(self):
        res = super(ConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()

        res.update({
            "enable_partner_credit_limit_block": params.get_param("sale.enable_partner_credit_limit_block"),
            "enable_partner_limit_key": params.get_param("sale.enable_partner_limit_key"),
        })

        return res
