from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_order_type_id = fields.Many2one('purchase.order.type', string='Tipo de orden de compra')