import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    target_currency_id = fields.Many2one(
        string="Divisa Objetivo",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id,
        compute="_compute_target_currency_id",
        readonly=True,
    )
    locked_currency_rate = fields.Float(
        string="Tipo de cambio bloqueado",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo a la divisa seleccionada y al tipo de cambio oficial del día.",
        compute="_compute_locked_currency_rate",
        default=lambda self: self.env.company.currency_id.inverse_rate,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            move.locked_currency_rate = 0
            if move.sale_order_count <= 0:
                continue
            for line in move.line_ids:
                source_order_id = line.sale_line_ids.order_id
                source_order = self.env["sale.order"].search([("id", "=", source_order_id.id)])
                if source_order:
                    move.locked_currency_rate = source_order.locked_currency_rate
        return moves

    @api.depends("sale_order_count")
    def _compute_target_currency_id(self):
        for move in self:
            move.locked_currency_rate = 0
            move.target_currency_id = False
            if move.state == "posted": 
                continue
            if move.sale_order_count <= 0:
                continue
            for line in move.line_ids:
                source_order_ids = line.sale_line_ids.order_id.ids
                source_orders = self.env["sale.order"].search([("id", "in", source_order_ids)])
                if source_orders:
                    order = source_orders.sorted(key=lambda r: r.date_order, reverse=True)[0]
                    move.target_currency_id = order.target_currency_id

    @api.depends("currency_id")
    def _compute_locked_currency_rate(self):
        for move in self:
            move.locked_currency_rate = 0
            if move.state == "posted":
                continue
            if move.sale_order_count <= 0:
                continue
            for line in move.line_ids:
                source_order_ids = line.sale_line_ids.order_id.ids
                source_orders = self.env["sale.order"].search([("id", "in", source_order_ids)])
                if source_orders:
                    order = source_orders.sorted(key=lambda r: r.date_order, reverse=True)[0]
                    move.locked_currency_rate = self.env["res.currency"].search([("id", "=", order.target_currency_id.id)], limit=1).inverse_rate
