from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_order_type_id = fields.Many2one('purchase.order.type', string='Tipo de orden de compra')

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()

        if self.purchase_order_type_id:
            res['location_id'] = self.purchase_order_type_id.location_id
            
        return res
