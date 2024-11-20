from odoo improt models, fields, api

class ProjectPlanWizardLine(models.TransientModel):

    _name = 'project.plan.wizard.line'
    _description = 'Project plan wizard line'

    wizard_id = fields.Many2one('project.creation.wizard', string="Wizard")
    name = fields.Char(string="Name", required=True)
    chapter = fields.Char(string="Chapter")
    description = fields.Text(string="Description")
    use_project_task = fields.Boolean(string="Use Project Task")
    planned_date_begin = fields.Datetime(string="Planned Start Date")
    planned_date_end = fields.Datetime(string="Planned End Date")
    partner_id = fields.Many2one('res.partner', string="Partner")
    task_timesheet_id = fields.Many2one('account.analytic.line', string="Timesheet Task")
    stage_id = fields.Many2one('project.task.type', string="Stage")