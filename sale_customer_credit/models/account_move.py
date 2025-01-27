import logging
from odoo import api, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        moves._check_and_update_partner_credit()
        return moves

    @api.onchange("partner_id")
    def _onchange_partner_set_addresses_default(self):
        for move in self:
            move.partner_shipping_id = move.partner_id

    def _check_and_update_partner_credit(self):
        # Agrupar por cliente para evitar llamadas redundantes
        partners = self.mapped('partner_id')
        for partner in partners:
            moves = self.filtered(lambda m: m.partner_id == partner)
            total_residual = sum(moves.mapped('amount_residual'))
            if not partner._check_credit_limit(total_residual):
                partner.customer_credit_suspend = True