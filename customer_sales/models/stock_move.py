from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import date
logger = logging.getLogger(__name__)


class BranchStockMove(models.Model):
    """inherited stock.move"""
    _inherit = 'stock.move'

    branch_id = fields.Many2one('res.partner', readonly=True, store=True,
                                related='picking_id.branch_id')

    def _compute_price_unit(self):
        for move in self:
            branch_id = self.env.user.branch_id.id
            move.product_id.get_branch_standard_price(branch_id)


class BranchStockMoveLine(models.Model):
    """inherited stock move line"""
    _inherit = 'stock.move.line'

    branch_id = fields.Many2one('res.partner', readonly=True, store=True,
                                related='move_id.branch_id')
