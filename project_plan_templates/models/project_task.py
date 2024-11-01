from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    description = fields.Text(string='Description')
    planned_date_begin = fields.Datetime(string='Planned Start Date')
    planned_date_end = fields.Datetime(string='Planned End Date')
    partner_id = fields.Many2one('res.partner', string='Partner')
