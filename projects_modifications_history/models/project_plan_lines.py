from odoo import fields, models, api

class ProjectPlanLines(models.Model):

    _inherit = 'project.plan.lines'

    project_version_id = fields.Many2one('project_version_history', string="Project Version")