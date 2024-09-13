from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_products_ids = fields.Many2many('product.template', string='Supplier Products')