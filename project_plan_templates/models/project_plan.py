from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Name", required=True)
    project_name = fields.Char(string="Project name", required=True)
    description = fields.Html(string="Description")
    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Project")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")

    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        string="Picking Lines",
        compute='_compute_picking_lines'
    )

    @api.onchange('project_plan_pickings')
    def _compute_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines

    def action_open_create_project_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create Project',
            'view_mode': 'form',
            'res_model': 'project.creation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_plan_id': self.id
            }
        }