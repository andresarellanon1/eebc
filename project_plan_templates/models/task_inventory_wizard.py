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
    product_packaging_id = fields.Many2one('product.packaging', 'Packaging', domain="[('product_id', '=', product_id)]", check_company=True)
    


    
    
    @api.onchange('stock_picking_ids')
    def _compute_fields(self):
        for record in self:
            _logger.warning('ENTRÓ A LOS CAMPOS COMPUTADOS')
            picking = record.stock_picking_ids[:1]
            record.picking_type_id = picking.picking_type_id
            record.location_id = picking.location_id
            record.location_dest_id = picking.location_dest_id
            record.task_id = picking.task_id