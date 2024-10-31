from odoo import models, fields, api

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
                
                task.stock_ids = stock_moves.filtered(lambda m: m.origin == task.name)
            else:
                task.stock_ids = False

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