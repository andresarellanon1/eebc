from odoo import fields, models, api

class TaskTimeLines(models.Model):

    _name = 'task.time.lines'
    _description = 'Project plan time lines model'

    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")

    description = fields.Char(string="Descripción", required=True)
    estimated_time = fields.Float(string="Horas estimadas")
    