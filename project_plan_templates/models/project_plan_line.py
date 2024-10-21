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
    product_uom = fields.Many2one('uom.uom', string="Unit of mesure")
    unit_price = fields.Float(string="Unit price")
    amount_total = fields.Float(string="Amount total")
    use_project_task = fields.Boolean(default=True)
    stage_id = fields.Char(string="Stage")
    planned_date_begin = fields.Date(default=fields.Date.context_today, string="Begin date")
    origin_project_id = fields.Many2one('project.project', string="Project")
    partner_id = fields.Many2one('res.users', string="Assinged user")

    def action_preview_task(self):
        task_vals = {
            'name': self.name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'description': self.description,
            'planned_date_begin': self.planned_date_begin,
        }
        task = self.env['project.task'].create(task_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'new',
        }