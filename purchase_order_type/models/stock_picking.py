from odoo import _, fields, models, api
import logging

logger = logging.getLogger(__name__)

class StockPiking(models.Model):
    _inherit = "stock.picking"

    @api.depends('picking_type_id', 'partner_id', 'purchase_id')
    def _compute_location_id(self):
        super(StockPiking, self)._compute_location_id()
        for picking in self:
            if picking.purchase_id and picking.purchase_id.purchase_order_type_id:
                picking.location_dest_id = picking.purchase_id.purchase_order_type_id.location_id
