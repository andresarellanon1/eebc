from odoo import fields, models, api

class TaskTimeLines(models.Model):

    _name = 'task.time.lines'
    _description = 'Project plan time lines model'

    task_timesheet_id = fields.Many2one('task.timesheet', string="Timesheet")

    description = fields.Char(string="Description", required=True)
    estimated_time = fields.Float(string="Estimated hours")
    