from odoo import fields, models, api
from datetime import datetime

class ProjectLines(models.Model):

    _name = 'project.plan.line'
    _description = 'Project plan lines'
 
    name = fields.Char(string="Name")
    chapter = fields.Char(string="Chapter", required=True)
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Description")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    project_id = fields.Many2one('project.project', string="Project")
    product_uom = fields.Many2one('uom.uom', string="Unit of mesure")
    unit_price = fields.Float(string="Unit price")
    amount_total = fields.Float(string="Amount total")
    use_project_task = fields.Boolean(default=True, string="Use task")
    stage_id = fields.Selection(
        string="Stage",
        selection=[('first', 'First stage'), ('second', 'Second stage'), ('third', 'Third stage')]
        )
    planned_date_begin = fields.Datetime(default=fields.Date.context_today, string="Begin date")
    planned_date_end = fields.Datetime(default=fields.Date.context_today, string="End date")
    origin_project_id = fields.Many2one('project.project', string="Project")
    partner_id = fields.Many2many('res.users', string="Assigned user")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Timesheet")

    # This action allows the user to preview how the task will look for a specific line.
    # It creates a temporary task using the details of the current line, such as the name, 
    # assigned users, description, planned start date, and deadline. 
    # The preview opens in a form view as a modal dialog, showing the task details 
    # without permanently saving the task in the project.
    
    def action_preview_task(self):
        user_ids = [partner.id for partner in self.partner_id] if self.partner_id else []

        task_vals = {
            'name': self.name,
            'user_ids': [(6, 0, user_ids)] if user_ids else False,
            'description': self.description,
            'planned_date_begin': self.planned_date_begin,
            'date_deadline': self.planned_date_end,
        }
        task = self.env['project.task'].create(task_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'new',
        }