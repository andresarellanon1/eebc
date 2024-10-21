from odoo import fields, api, models
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    #project_plan_id = fields.One2many('project.plan', 'project_id', string="Project template")
    project_plan_description = fields.Char(string="Project description")
    #project_plan_lines = fields.One2many('project.plan.line', 'project_id', string="Project plan lines")

    