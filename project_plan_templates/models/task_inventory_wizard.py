from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProjectCreation(models.TransientModel):
    _name = 'task.inventory.wizard'
    _description = 'Wizard to confirm project creation'

    
    project_task_id = fields.Many2one('project.task', string="Project Task")
    
    stock_move_ids = fields.Many2many('stock.move', string="Stock move")

    stock_picking_ids = fields.Many2many('stock.picking', string="Stock picking")

    # stock_move_id = fields.Many2many('stock.move', string="Stock move" )

    name = fields.Char(string='Referencia')
    partner_id = fields.Many2one('res.partner',  string='Contacto')
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación')
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen')
    task_id = fields.Many2one('stock.picking', string='Tarea de origen')
    modified_by = fields.Many2one('res.users', string='Contacto')
    product_packaging_id = fields.Many2one('product.packaging', 'Packaging', domain="[('product_id', '=', product_id)]", check_company=True)
    
    # Sección de Información adicional

    carrier_id = fields.Many2one('delivery.carrier')
    carrier_tracking_ref = fields.Char(string="Referencia de rastreo")
    weight = fields.Float(string="Peso")
    shipping_weight = fields.Float(string="Peso para envío")

    group_id = fields.Many2one('procurement.group', string="Grupo de aprovisionamiento")
    company_id = fields.Many2one('res.company', string="Empresa")
    
    transport_type = fields.Selection( string="Tipo de transporte",
        selection=[('00', 'No usa carreteras federales'), ('01', 'Autotransporte Federal')])
    # customs regimes
    # customs document type
    custom_document_identification = fields.Char(string="Customs Document Identification")

    lat_origin = fields.Float(string="Latitud de origen")
    long_origin = fields.Float(string="Longitud de origen")
    lat_dest = fields.Float(string="Latitud de destino")
    long_dest = fields.Float(string="Longitud de destino")


    @api.onchange('stock_picking_ids')
    def _compute_fields(self):
        for record in self:
            _logger.warning('ENTRÓ A LOS CAMPOS COMPUTADOS')
            record.task_id = project_task_id.id


    def action_confirm_create_inventory(self):
            self.ensure_one()
            stock_picking_ids_vals = [(0, 0, {
                'name': line.name,
                'partner_id': line.partner_id.id,
                'picking_type_id': line.picking_type_id.id,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'scheduled_date': line.scheduled_date,
                'origin': line.origin,
                'task_id': line.task_id.id,
                'modified_by': line.modified_by,
                'product_packaging_id': line.product_packaging_id.id,
                
                'carrier_id': line.carrier_id.id,
                'carrier_tracking_ref': line.carrier_tracking_ref,

                'weight': line.weight,
                'shipping_weight': line.shipping_weight,
                'group_id': line.group_id.id,
                'company_id': line.company_id.id,
                'transport_type': line.transport_type,
                'custom_document_identification': line.custom_document_identification,
                'lat_origin': line.lat_origin,
                'long_origin': line.long_origin,
                'lat_dest': line.lat_dest,
                'long_dest': line.long_dest,
            }) for line in self.stock_picking_ids]

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'res_id': stock_picking_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
