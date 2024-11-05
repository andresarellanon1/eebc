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

    partner_id = fields.Many2one('res.users',  string='Contacto')
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación')
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen')
    task_id = fields.Many2one('stock.picking', string='Tarea de origen')
    modified_by = fields.Many2one('res.users', string='Contacto')
    
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