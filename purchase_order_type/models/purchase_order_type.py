from odoo import _, fields, models, api
import logging
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Tipo de orden de compra"

    name = fields.Char('Nombre', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación')
    company_id = fields.Many2one('res.company', string='Empresa')