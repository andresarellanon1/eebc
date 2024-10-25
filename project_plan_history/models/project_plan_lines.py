from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = 'project.plan.line'

    version_id = fields.Many2one('project.version', string="History ")