from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import date
logger = logging.getLogger(__name__)


class BranchStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    branch_id = fields.Many2one('res.branch',
                                readonly=True,
                                store=True,
                                related='stock_move_id.branch_id')
