from odoo import fields, models, api

class ProjectTask(models.Model):
   
    _inherit = 'project.task'


    def action_open_task_inventory_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create inventory',
            'view_mode': 'form',
            'res_model': 'task.inventory.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_stock_picking_id': self.id.stock_ids
            }
        }

    # stock.move (picking_id) - stock.picking (task_id) - project.task (project_id) - project.project (project_picking_lines) project.project (project_picking_ids)