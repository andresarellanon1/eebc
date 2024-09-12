from odoo import _, fields, models
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "purchase.order"

    purchase_order_notice_id = fields.Many2one('notices.notices', string='Registro de orden de compra avisos')

