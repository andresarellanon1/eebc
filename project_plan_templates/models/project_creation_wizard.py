from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Project Plan", required=True)
    project_name = fields.Char(related='project_plan_id.project_name', string="Project Name")
    user_id = fields.Many2one('res.users', string="Project manager")

    def action_confirm_create_project(self):
        self.ensure_one()
        
        return self.project_plan_id.action_create_project()