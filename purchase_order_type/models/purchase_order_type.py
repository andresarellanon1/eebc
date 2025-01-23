from odoo import fields, models
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Tipo de orden de compra"

    name = fields.Char('Nombre', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación', required=True)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, default=lambda self: self.env.company.id)
