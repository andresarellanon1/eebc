from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    chapter = fields.Char(string='Chapter')
    description = fields.Text(string='Description')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    unit_price = fields.Float(string='Unit Price')
    amount_total = fields.Float(string='Total Amount')
    use_project_task = fields.Boolean(string='Use Project Task')
    stage_id = fields.Many2one('project.task.type', string='Stage')
    planned_date_begin = fields.Datetime(string='Planned Start Date')
    planned_date_end = fields.Datetime(string='Planned End Date')
    origin_project_id = fields.Many2one('project.project', string='Origin Project')
    partner_id = fields.Many2one('res.partner', string='Partner')
    task_timesheet_id = fields.Many2one('account.analytic.line', string='Task Timesheet')
