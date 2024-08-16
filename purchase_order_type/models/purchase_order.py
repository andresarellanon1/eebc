from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_order_type_id = fields.Many2one('purchase_order_type.purchase_order_type', string='Tipo de Orden de Compra', required=True)