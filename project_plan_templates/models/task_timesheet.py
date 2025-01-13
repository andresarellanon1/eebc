from odoo import fields, models, api

class TaskTimesheet(models.Model):

    _name = 'task.timesheet'
    _description = 'Templates for tasks timesheets'

    name = fields.Char(string="Nombre de plantilla", required=True)
    description = fields.Html(string="Descripción")

    task_time_lines = fields.One2many('task.time.lines', 'task_timesheet_id')
    