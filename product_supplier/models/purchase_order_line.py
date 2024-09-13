from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_ids = fields.Many2many('product.product', store=True)