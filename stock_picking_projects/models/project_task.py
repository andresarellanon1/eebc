from odoo import models, fields, api

class ProjectTask(models.Model):

    _inherit = 'project.task'

    stock_ids = fields.One2many('stock.picking', 'project_id', string="stock")
    move_ids = fields.One2many('stock.move', 'task_id', string="Lineas de operaciones")

    @api.depends('project_id.default_picking_type_id')
    def _compute_stock_ids(self):
        for task in self:
            if task.project_id.default_picking_type_id:
                picking_type_id = task.project_id.default_picking_type_id.id
                
                stock_moves = self.env['stock.move'].search([
                    ('picking_type_id', '=', picking_type_id),
                    ('project_id', '=', task.project_id.id)
                ])
                
                task.stock_ids = stock_moves
            else:
                task.stock_ids = False