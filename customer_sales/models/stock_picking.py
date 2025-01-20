from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import date
logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """inherited stock.picking"""
    _inherit = "stock.picking"

    branch_id = fields.Many2one("res.branch",
                                string='Branch',)
