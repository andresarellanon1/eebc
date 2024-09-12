from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    account_move_notice_id = fields.Many2one('account.move', string='Facturas de avisos')

