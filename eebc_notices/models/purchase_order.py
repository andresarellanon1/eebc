from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "purchase.order"

    notice_id = fields.Many2one(
        comodel_name='notices.notices',
        string='Aviso relacionado'
    )

    notice_file_wizard_id = fields.Many2one(
        comodel_name='notice.file.wizard',
        
    )

