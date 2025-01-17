from odoo import api, fields, models
import logging
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    target_currency_id = fields.Many2one(
        string="Divisa Objetivo",
        help='Divisa Objetivo. Depende de la Divisa Objetivo de la orden padre.',
        comodel_name='res.currency'
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleOrderLine, self).create(vals_list)
        for line in lines:
            line.target_currency_id = line.order_id.target_currency_id

        return lines
