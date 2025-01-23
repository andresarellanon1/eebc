from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    sales_currency_id = fields.Many2one(
        string="Divisa de venta",
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    priority_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Lista de precio prioritaria',
        help='Lista de precios con prioridad para este cliente.')
