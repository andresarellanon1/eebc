from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'task.inventory.wizard'
    _description = 'Wizard to confirm project creation'

    
    project_task_id = fields.Many2one('project.task', string="Project Task")
    stock_picking_ids = fields.Many2many('stock.picking', string="Stock picking")
    
    # stock_move_id = fields.Many2many('stock.move', string="Stock move")

    partner_id = fields.Char(string='Contacto')
    picking_type_id = fields.Char(string='Tipo de operación')
    location_id = fields.Char(string='Ubicación de origen')
    location_dest_id = fields.Char(string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen')
    task_id = fields.Char(string='Tarea de origen')


    @api.onchange('stock_picking_ids')
    def _compute_fields(self):
        for record in self:
            record.partner_id = record.stock_picking_ids.name
            record.picking_type_id = record.stock_picking_ids.picking_type_id
            record.location_id = record.stock_picking_ids.location_id
            record.location_dest_id = record.stock_picking_ids.location_dest_id
            record.scheduled_date = record.stock_picking_ids.scheduled_date
            record.origin = record.stock_picking_ids.origin
            record.task_id = record.stock_picking_ids.task_id