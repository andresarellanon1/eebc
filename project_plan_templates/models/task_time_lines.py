from odoo import fields, models, api

class TaskTimeLines(models.Model):

    _name = 'task.time.lines'
    _description = 'Project plan time lines model'

    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")
    task_time_lines_id = fields.Many2one('project.picking.lines', string="Lineas de trabajo")
    

    description = fields.Char(string="Descripción", required=True)
    estimated_time = fields.Float(string="Horas estimadas")
    work_shift = fields.Float(string='Jornadas Laborales')
    

    @api.onchange('work_shift')
    def _work_shift_onchange_(self):
        for record in self:
            record.estimated_time = record.work_shift * 8