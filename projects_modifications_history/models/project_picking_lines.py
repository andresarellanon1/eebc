from odoo import fields, models, api

class ProjecPickingLines(models.Model):
    
    _inherit = 'project.picking.lines'

    project_version_id = fields.Many2one('project_version_history', string="Project Version")