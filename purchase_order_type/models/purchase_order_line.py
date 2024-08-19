from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)

        if self.order_id and self.order_id.purchase_order_type_id:
            res['location_dest_id'] = self.purchase_order_type_id.location_id.id

        return res