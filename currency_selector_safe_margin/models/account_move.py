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


# def action_view_source_sale_orders(self):
#         self.ensure_one()
#         source_orders = self.line_ids.sale_line_ids.order_id
#         result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
#         if len(source_orders) > 1:
#             result['domain'] = [('id', 'in', source_orders.ids)]
#         elif len(source_orders) == 1:
#             result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
#             result['res_id'] = source_orders.id
#         else:
#             result = {'type': 'ir.actions.act_window_close'}
#         return result
