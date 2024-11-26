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
    is_picking_type_enabled = fields.Boolean(string='Utilizar Tipos de operación', default=True)

    @api.onchange('is_picking_type_enabled')
    def _onchange_is_picking_type_enabled(self):
        for record in self:
            if not record.is_picking_type_enabled: record.picking_type_id = False