import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    locked_currency_rate = fields.Float(
        string="Tipo de cambio bloqueado",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo a la divisa seleccionada y al tipo de cambio oficial del día.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.sale_order_count > 0:
                for line in move.line_ids:
                    source_order_id = line.sale_line_ids.order_id
                    source_order = self.env["sale.order"].search([("id", "=", source_order_id.id)])
                    move.locked_currency_rate = source_order.locked_currency_rate

            else:
                move.onchange_currency_rate()
        return moves

    @api.onchange("currency_id")
    def onchange_currency_rate(self):
        if self.state == "posted":
            return
        else:
            self.locked_currency_rate = self.env["res.currency"].search([("name", "=", "USD")], limit=1).inverse_rate
