from odoo import fields, models, api

class ProjectTask(models.Model):
   
    _inherit = 'project.task'
    
    stock_ids = fields.One2many('stock.picking', 'task_id', string="stock")

    def action_open_task_inventory_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create inventory',
            'view_mode': 'form',
            'res_model': 'task.inventory.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_task_id': self.id,
                'task_id': self.id,
                'default_stock_picking_ids': [(6, 0, self.stock_ids.ids)],
                'default_user_id': self.env.user.id,
                'default_stock_move_ids': [(6, 0, self.stock_ids.move_ids.ids)],
            }
        }

# stock.move (picking_id) - stock.picking (task_id) - project.task (project_id) - project.project (project_picking_lines) project.project (project_picking_ids)

    def action_create_inventory(self):
        inventory_vals = {
            'origin': self.name,
            'picking_type_id': self.project_id.default_picking_type_id.id,
            'task_id': self.id,
        }
        inventory = self.env['stock.picking'].create(inventory_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'new',
        }