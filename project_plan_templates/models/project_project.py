from odoo import fields, api, models
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    project_plan_id = fields.One2many('project.plan', 'project_id',string="Project template")
    project_plan_description = fields.Char(string="Project description")
    project_plan_lines = fields.One2many('project.plan.line', 'project_id', string="Project plan lines")

    @api.depends('project_plan_id')
    def plan_lines(self):
        for project in self:
            if project.project_plan_id:
                project.project_plan_lines = project.project_plan_id.plan_line_ids
                project.project_plan_description = project.project_plan_id.description
            else:
                project.project_plan_lines = [(5, 0, 0)]

    #def action_create_tasks(self):
    #    tasks_vals = {
    #        'name': self.name
    #    }
