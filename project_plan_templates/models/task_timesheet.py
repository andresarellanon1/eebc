from odoo import fields, models, api

class TaskTimesheet(models.Model):

    _name = 'task.timesheet'
    _description = 'Templates for tasks timesheets'

    name = fields.Char(string="Nombre de plantilla", required=True)
    description = fields.Html(string="Descripción")

    task_time_lines = fields.One2many('task.time.lines', 'task_timesheet_id')

    labour_total_cost = fields.Float(string="Costo mano de obra", compute="_compute_labour_cost", default=0.0)

    @api.depends('task_time_lines.price_subtotal')
    def _compute_labour_cost(self):
        for task in self:
            task.labour_total_cost = sum(line.price_subtotal for line in task.task_time_lines)