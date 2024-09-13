from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "purchase.order"

    notice_id = fields.Many2one(
        comodel_name='notices.notices',
        string='Aviso relacionado'
    )