from odoo import _, fields, models, api
import logging

logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_ids = fields.Many2many(comodel_name='project.project', string='Proyectos')

    @api.onchange('purchase_order_type_id')
    def _onchange_purchase_order_type_id(self):
        for record in self:
            super(PurchaseOrder, record)._onchange_purchase_order_type_id()
            
            if record.id != 1: record.project_ids = False