from odoo import _, fields, models, api
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_order_type_id = fields.Many2one('purchase.order.type', string='Tipo de orden de compra')
    is_picking_type_enabled = fields.Boolean(related='purchase_order_type_id.is_picking_type_enabled')

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()

        if self.purchase_order_type_id and not self.pis_picking_type_enabled:
            res['location_dest_id'] = self.purchase_order_type_id.location_id.id

        return res
    
    @api.onchange('purchase_order_type_id')
    def _onchange_purchase_order_type_id(self):
        for record in self:
            if not record.purchase_order_type_id.picking_type_id:
                continue

            record.picking_type_id = record.purchase_order_type_id.picking_type_id
