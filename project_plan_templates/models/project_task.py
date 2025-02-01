from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    stock_ids = fields.One2many(
        'stock.picking',
        'task_id',
        string="Inventario"
    )

    project_picking_lines = fields.One2many('project.picking.lines', 'task_id')

    task_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    allocated_hours = fields.Float(compute="_compute_allocated_hours")

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.task_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

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
                'default_user_id': self.env.user.id,
            }
        }

    @api.depends('timesheet_ids.estimated_time')
    def _compute_allocated_hours(self):
        for record in self:
            record.allocated_hours = sum(record.timesheet_ids.mapped('estimated_time'))