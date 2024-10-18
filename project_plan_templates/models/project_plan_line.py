from odoo import fields, name, models

class ProjectLines(models.Model):

    _name = 'project.plan.line'
    _description = 'Project plan lines'

    name = fields.Char(string="Name")
    chapter = fields.Char(string="Chapter", required=True)
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Description")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")