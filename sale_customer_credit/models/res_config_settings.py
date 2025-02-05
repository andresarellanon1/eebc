from odoo import fields, models
import logging
logger = logging.getLogger(__name__)


class ConfigSettings(models.TransientModel):
    """Extiende el modelo res.config.settings para agregar opciones de configuración relacionadas con la gestión de crédito de los partners."""

    _inherit = "res.config.settings"

    enable_partner_credit_limit_block = fields.Boolean(string="Bloquear ventas a clientes por límite de crédito excedido.")
    enable_partner_limit_key = fields.Boolean(string="Permite el uso de la llave de crédito para confirmar cotizaciones que sobrepasan el límite de crédito del cliente.")

    def set_values(self):
        """
        Establece los valores de los parámetros de configuración.

        1. Llama al método set_values del modelo base para garantizar la herencia.
        2. Obtiene la referencia al modelo ir.config_parameter.
        3. Configura los parámetros sale.enable_partner_credit_limit_block y sale.enable_partner_limit_key
           con los valores actuales de los campos en la vista de configuración.
        """
        super(ConfigSettings, self).set_values()
        params = self.env["ir.config_parameter"]
        params.set_param("sale.enable_partner_credit_limit_block", self.enable_partner_credit_limit_block)
        params.set_param("sale.enable_partner_limit_key", self.enable_partner_limit_key)

    def get_values(self):
        """
        Obtiene los valores de los parámetros de configuración.

        1. Llama al método get_values del modelo base para garantizar la herencia.
        2. Obtiene los valores de los parámetros sale.enable_partner_credit_limit_block y sale.enable_partner_limit_key
           desde ir.config_parameter utilizando sudo para garantizar permisos.
        3. Actualiza el diccionario de resultados con los valores obtenidos.

        Returns:
            dict: Un diccionario con los valores de configuración.
        """
        res = super(ConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()

        res.update({
            "enable_partner_credit_limit_block": params.get_param("sale.enable_partner_credit_limit_block", default=False),
            "enable_partner_limit_key": params.get_param("sale.enable_partner_limit_key", default=False),
        })

        return res