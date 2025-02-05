from odoo import api, fields, models

import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    target_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Divisa Objetivo",
        store=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    locked_currency_rate = fields.Float(
        string="Tipo de cambio",
        digits="Payment Terms",
        help="El tipo de cambio se calcula de acuerdo a la divisa seleccionada y al tipo de cambio oficial del día.",
        compute="_compute_locked_currency_rate",
        default=lambda self: self.env.company.currency_id.inverse_rate,
        store=True,
        readonly=True,
    )

    @api.depends("target_currency_id", "target_currency_id.inverse_rate")
    def _compute_locked_currency_rate(self):
        for order in self:
            if order.state == "done":
                continue
            order.locked_currency_rate = order.target_currency_id.inverse_rate
            for line in order.order_line:
                line._product_id_change()

    @api.onchange("target_currency_id")
    def onchange_target_currency_id(self):
        """
            Updates the field currency_id when the target currency changes.
        """
        for order in self:
            if order.state == "done":
                continue
            order.currency_id = order.target_currency_id
