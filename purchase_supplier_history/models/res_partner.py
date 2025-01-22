from odoo import models, fields
import logging
logger = logging.getLogger(__name__)


class respartner(models.Model):
    _inherit = "res.partner"

    is_supplier = fields.Boolean(default=False, string="Es proveedor")
    supplier_number_reference = fields.Char(string="Referencia de proveedor")
    lead_time = fields.Integer(string='Lead Time', help='Tiempo de entrega', default=3)
