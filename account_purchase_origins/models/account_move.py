import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    origin_purchase_ids = fields.Many2many('purchase.order',
                                           store=True,
                                           readonly=False,
                                           string='Purchase Orders',
                                           compute="_compute_origin_purchase_ids",
                                           help="")

    @api.depends('line_ids')
    def _compute_origin_purchase_ids(self):
        for move in self:
            purchase_ids = {line.purchase_line_id.order_id.id for line in move.line_ids if line.purchase_line_id}
            if purchase_ids:
                origins = self.env['purchase.order'].browse(purchase_ids)
                move.origin_purchase_ids = [(6, 0, origins.ids)]
            else:
                move.origin_purchase_ids = [(5, 0, 0)]
