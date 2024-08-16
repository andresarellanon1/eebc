from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Tipo de Orden de Compra"

    name = fields.Char('Tipo de Orden de Compra', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación', required=True)
