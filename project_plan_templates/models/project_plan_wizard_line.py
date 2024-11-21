from odoo import models, fields, api

class ProjectPlanWizardLine(models.TransientModel):

    _name = 'project.plan.wizard.line'
    _description = 'Project plan wizard line'

    wizard_id = fields.Many2one('project.creation.wizard', string="Wizard")
    name = fields.Char(string="Name")
    chapter = fields.Char(string="Chapter")
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Description")
    use_project_task = fields.Boolean(string="Use Project Task")
    planned_date_begin = fields.Datetime(string="Planned Start Date")
    planned_date_end = fields.Datetime(string="Planned End Date")
    partner_id = fields.Many2many('res.users', string="Assigned user")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Timesheet Task")
    stage_id = fields.Many2one(
        'project.task.type',
        string="Stage",
    )
    project_plan_id = fields.Many2one('project.plan', string="Project plan")