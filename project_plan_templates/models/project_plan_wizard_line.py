from odoo import models, fields, api

# Transient model for managing project plan wizard lines. 
# This model temporarily stores project task configurations 
# during the project creation process, including task details,
# assignments, and scheduling information.
class ProjectPlanWizardLine(models.TransientModel):
    _name = 'project.plan.wizard.line'
    _description = 'Project plan wizard line'

    # Relation fields
    wizard_id = fields.Many2one('project.creation.wizard', string="Wizard")
    partner_id = fields.Many2many('res.users', string="Assigned user")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Timesheet Task")

    # Task information fields
    name = fields.Char(string="Name")
    chapter = fields.Char(string="Chapter")
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Description")
    use_project_task = fields.Boolean(string="Use Project Task")

    # Schedule fields
    planned_date_begin = fields.Datetime(string="Planned Start Date")
    planned_date_end = fields.Datetime(string="Planned End Date")

    display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    code = fields.Char(string="Code")
    sequence = fields.Integer()