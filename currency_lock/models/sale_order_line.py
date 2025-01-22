from odoo import api, fields, models
import logging
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    target_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Divisa Objetivo",
        related="order_id.target_currency_id",
        help='Divisa Objetivo. Depende de la Divisa Objetivo de la orden padre.',
    )
