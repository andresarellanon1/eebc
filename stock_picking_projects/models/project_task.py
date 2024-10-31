from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    stock_ids = fields.One2many('stock.move', 'task_id', string="Stock")

    @api.depends('project_id.default_picking_type_id')
    def _compute_stock_ids(self):
        for task in self:
            if task.project_id.default_picking_type_id:
                picking_type_id = task.project_id.default_picking_type_id.id
                stock_moves = self.env['stock.move'].search([
                    ('picking_type_id', '=', picking_type_id),
                    ('task_id', '=', task.id)
                ])
                task.stock_ids = stock_moves
            else:
                task.stock_ids = False

    def action_create_inventory(self):
        inventory_vals = {
            'origin': self.name,
            'picking_type_id': self.project_id.default_picking_type_id.id,
            'task_id': self.id,
            'move_lines': [(0, 0, {
                'product_id': move.product_id.id,
                'product_packaging_id': move.product_packaging_id.id,
                'product_uom_qty': move.product_qty,
                'product_uom': move.product_uom.id,
                'picking_type_codigo': move.picking_type_codigo.id,
            }) for move in self.stock_ids if move.product_qty > 0]
        }
        
        inventory = self.env['stock.picking'].create(inventory_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'new',
        }
