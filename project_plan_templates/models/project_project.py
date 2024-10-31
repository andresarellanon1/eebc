from odoo import fields, api, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Project template", readonly="True")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines")

    def action_create_tasks(self):
        for project in self:
            for line in project.project_plan_lines:
                project.env['project.task'].create({
                    'name': line.name,
                    'project_id': project.id,
                    'planned_hours': line.planned_hours,
                    'user_id': line.user_id.id,
                    'date_deadline': line.date_deadline,
                    'description': line.description,
                })