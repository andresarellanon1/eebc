import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    purchase_order_ids = fields.Many2many("purchase.order")

    @api.onchange('purchase_order_ids')
    def onchange_purchase_orders(self):
        for record in self:
            for order in record.purchase_order_ids:
                order._update_landed_in_lines()