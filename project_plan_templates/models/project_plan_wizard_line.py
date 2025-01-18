from odoo import models, fields, api


class ProjectPlanWizardLine(models.TransientModel):
    _name = 'project.plan.wizard.line'
    _description = 'Project plan wizard line'
    _order = 'sequence'

    wizard_id = fields.Many2one('project.creation.wizard', string="Wizard")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")
    wizard_version_id = fields.Many2one('project.version.wizard', string="Wizard history")

    name = fields.Char(string="Tarea")
    chapter = fields.Char(string="Chapter")
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Descripción")
    use_project_task = fields.Boolean(string="Usar tarea")

    planned_date_begin = fields.Datetime(string="Fecha de incio")
    planned_date_end = fields.Datetime(string="Fecha de finalización")

    display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    code = fields.Char(string="Code")
    sequence = fields.Integer()
    project_plan_pickings = fields.Many2one('project.plan.pickings', string="Movimientos de inventario")
    for_create = fields.Boolean()