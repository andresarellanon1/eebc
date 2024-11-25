from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    stock_ids = fields.One2many(
        'stock.picking',
        'task_id',
        string="stock"
    )

    # Defining a method to open an inventory wizard
    # (a form to create an inventory related to the task).
    def action_open_task_inventory_wizard(self):
        self.ensure_one()
        
        # Returns a dictionary representing an action
        # to open a new window with a specific form view.
        return {
            'name': 'Create inventory', 
            'view_mode': 'form',
            'res_model': 'task.inventory.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_task_id': self.id,
                'default_user_id': self.env.user.id,
            }
        }