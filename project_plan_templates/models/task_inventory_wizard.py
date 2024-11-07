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
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación', compute='_compute_picking_type_id', store=True)
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen', compute="_compute_origin", store=True)
    task_id = fields.Many2one('stock.picking', string='Tarea de origen')
    user_id = fields.Many2one('res.users', string='Contacto')
    
    
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

    @api.onchange('project_task_id')
    def _onchange_project_task_id(self):
        if self.project_task_id:
            project = self.project_task_id.project_id
            product_ids = project.project_picking_ids.mapped('project_picking_lines.product_id.id')
            return {'domain': {'stock_move_ids': [('product_id', 'in', product_ids)]}}

    @api.model
    def _compute_fields(self):
        for record in self:
            _logger.warning('ENTRÓ A LOS CAMPOS COMPUTADOS')
            record.task_id = project_task_id.id
    
    @api.model
    def default_get(self, fields_list):
        res = super(task.inventory.wizard, self).default_get(fields_list)
        
        # Asigna el valor de picking_type_id
        project_task_id = res.get('project_task_id')
        if project_task_id:
            task = self.env['project.task'].browse(project_task_id)
            if task.project_id.default_picking_type_id:
                res['picking_type_id'] = task.project_id.default_picking_type_id.id
                _logger.warning(f'El valor de picking_type_id es: {task.project_id.default_picking_type_id.id}')
        
        # Asigna el valor de origin
        if 'origin' in fields_list and project_task_id:
            res['origin'] = task.name
            _logger.warning(f'El valor de origin es: {task.name}')

        return res

    # def _compute_picking_type_id(self):
    #     _logger.warning(f'El valor de picking typ es: {project_task_id.project_id.default_picking_type_id}')
    #     record.picking_type_id = project_task_id.project_id.default_picking_type_id

    # def _compute_origin(self):
    #     _logger.warning(f'El valor de origin es: {project_task_id.name}')
    #     record.origin = project_task_id.name


    def action_confirm_create_inventory(self):
            self.ensure_one()
            stock_move_ids_vals = [(0, 0, {
                'product_id': line.product_id.id,
                'product_packaging_id': line.product_packaging_id.id,
                'product_uom_qty':line.product_uom_qty,
                'quantity':line.quantity,
                'product_uom':line.product_uom.id,
                'picking_type_codigo':line.picking_type_codigo,
                'location_id':line.location_id.id,
                'location_dest_id':line.location_dest_id.id,
                'name':line.name,

            }) for line in self.stock_move_ids]

            stock_picking_vals ={
                'name': self.name,
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'scheduled_date': self.scheduled_date,
                'origin': self.origin,
                'task_id': self.task_id.id,
                'user_id': self.user_id.id,
                'move_ids': stock_move_ids_vals,
                
                'carrier_id': self.carrier_id.id,
                'carrier_tracking_ref': self.carrier_tracking_ref,

                'weight': self.weight,
                'shipping_weight': self.shipping_weight,
                'group_id': self.group_id.id,
                'company_id': self.company_id.id,
                'transport_type': self.transport_type,
                'custom_document_identification': self.custom_document_identification,
                'lat_origin': self.lat_origin,
                'long_origin': self.long_origin,
                'lat_dest': self.lat_dest,
                'long_dest': self.long_dest,
            }

            stock_picking = self.env['stock.picking'].create(stock_picking_vals)
