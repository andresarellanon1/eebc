from odoo import _, fields, models, api
import logging
import logging

logger = logging.getLogger(__name__)

class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Tipo de orden de compra"

    name = fields.Char('Nombre', required=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación', default=False)
    company_id = fields.Many2one('res.company', string='Compañia', compute="_compute_company_id")
    location_id = fields.Many2one('stock.location', string='Ubicación', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Secuencia')

    is_picking_type_setting_enabled = fields.Boolean(
        compute="_compute_is_picking_type_setting_enabled"
    )

    def _compute_is_picking_type_setting_enabled(self):
        enable_purchase_picking_type_from_purchase_order_type = self.env["ir.config_parameter"].sudo().get_param("purchase.enable_purchase_picking_type_from_purchase_order_type")
        for record in self:
            record.is_picking_type_setting_enabled = enable_purchase_picking_type_from_purchase_order_type

    @api.depends('picking_type_id')
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.picking_type_id.company_id