from odoo import fields, models, api

class ProjectPlanLines(models.Model):

    _inherit = 'project.plan.line'
    _order = 'sequence'

    project_version_id = fields.Many2one('project.version.history', string="Project Version")