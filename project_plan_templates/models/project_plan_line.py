from odoo import fields, models, api
from datetime import datetime


class ProjectLines(models.Model):
   _name = 'project.plan.line'
   _description = 'Project plan lines'

   
   name = fields.Char(string="Name", default=False)
   chapter = fields.Char(string="Chapter")
   clave = fields.Integer(string="Task id")
   description = fields.Char(string="Description")
   use_project_task = fields.Boolean(default=True, string="Use task")

   
   project_plan_id = fields.Many2one('project.plan', string="Project plan")
   origin_project_id = fields.Many2one('project.project', string="Project")
   stage_id = fields.Many2one(
       'project.task.type',
       string="Stage",
   )
   partner_id = fields.Many2many('res.users', string="Assigned user")
   task_timesheet_id = fields.Many2one('task.timesheet', string="Timesheet")
   sale_order_id = fields.Many2one('sale.order', string="Origin")

  
   planned_date_begin = fields.Datetime(default=fields.Date.context_today, string="Begin date")
   planned_date_end = fields.Datetime(default=fields.Date.context_today, string="End date")

   display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
   )
   code = fields.Char(string="Code")
   sequence = fields.Integer()

   
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
    
    @api.constrains('planned_date_begin', 'planned_date_end')
    def _check_dates(self):
        for record in self:
            if record.planned_date_end and record.planned_date_begin:
                if record.planned_date_end < record.planned_date_begin:
                    raise ValidationError(
                        "La Fecha de finalización no puede ser anterior a la Fecha de inicio."
                    )