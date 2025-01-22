from odoo import fields, models
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_reference = fields.Char(string="Orden de compra", help="Referencia de la orden de compra del cliente. Este campo no representa una orden de compra dentro de odoo. Se refiere a una orden de compra en el sistema del cliente.")
