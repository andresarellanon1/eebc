from odoo import fields, models, api

class ProjectTask(models.Model):
   
    _inherit = 'project.task'

    stock_ids = fields.One2many('stock.picking', 'task_id', string="stock")

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
                

    def action_open_task_inventory_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create inventory',
            'view_mode': 'form',
            'res_model': 'task.inventory.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_stock_picking_id': self.stock_ids.id
            }
        }

    # stock.move (picking_id) - stock.picking (task_id) - project.task (project_id) - project.project (project_picking_lines) project.project (project_picking_ids)