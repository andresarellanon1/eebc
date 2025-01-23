from odoo import fields, models, api

class ProjectPlanLines(models.Model):

    _inherit = 'project.plan.line'
    _order = 'sequence'

    project_version_id = fields.Many2one('project_version_history', string="Project Version")