from odoo import fields, models, api

class ProjectPlanLines(models.TransientModel):
    _inherit = 'project.plan.line'

    version_id = fields.Many2one('project.version', string="History")