from odoo import fields, models, api

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Name", required=True)
    project_name = fields.Char(string="Project name")
    currency_id = fields.Many2one('res.currency', string="Currency")
    currency_rate = fields.Float(string="Currency rate", required="True")
    project_plan_line = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")

