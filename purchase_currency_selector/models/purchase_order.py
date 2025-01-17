import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    locked_currency_rate = fields.Float(
        string="Tipo de cambio",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo a la divisa seleccionada y al tipo de cambio oficial del día.",
    )

    @api.onchange("currency_id")
    def onchange_currency_rate(self):
        if self.state == "done":
            return
        else:
            locked_currency = self.env["ir.config_parameter"].sudo().get_param("sale.locked_currency")
            self.locked_currency_rate = self.env["res.currency"].search([("id", "=", locked_currency.id)], limit=1).inverse_rate
            for line in self.order_line:
                line._product_id_change()
