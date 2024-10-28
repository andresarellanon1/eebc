from odoo import fields, models, api

class ProjectPickingLines(models.Model):
    _inherit = 'project.picking.lines'

    version_id = fields.Many2one('project.version', string="History ")