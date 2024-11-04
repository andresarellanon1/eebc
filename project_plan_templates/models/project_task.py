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
                'default_stock_picking_id': self.id
            }
        }

