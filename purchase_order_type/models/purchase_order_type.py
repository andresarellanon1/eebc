from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Tipo de orden de compra"

    name = fields.Char('Nombre', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Secuencia', required=True)
