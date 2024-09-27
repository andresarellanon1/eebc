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

    def action_create_inventory(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['context'] = {
            'default_origin': self.name,
            'default_picking_type_id': self.project_id.default_picking_type_id.id,
            'default_task_id': self.id,
        }
        action['domain'] = [('task_id', '=', self.id)]
        return action