from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class ProjectLines(models.Model):
    _name = 'project.plan.line'
    _description = 'Project plan lines'
    _order = 'sequence'
    
    name = fields.Char(string="Tarea", default=False)
    chapter = fields.Char(string="Chapter")
    clave = fields.Integer(string="Task id")
    description = fields.Char(string="Descripción")
    use_project_task = fields.Boolean(default=True, string="Usar tarea")

    
    project_plan_id = fields.Many2one('project.plan', string="Plan de proyecto")
    origin_project_id = fields.Many2one('project.project', string="Proyecto")
    stage_id = fields.Many2one(
        'project.task.type',
        string="Stage",
    )
    partner_id = fields.Many2many('res.users', string="Usuarios asignados")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas", required=True)
    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")

    
    planned_date_begin = fields.Datetime(default=fields.Date.context_today, string="Fecha de inicio")
    planned_date_end = fields.Datetime(default=fields.Date.context_today, string="Fecha de finalización")

    display_type = fields.Selection(
            [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    code = fields.Char(string="Code")
    sequence = fields.Integer()
    project_plan_pickings = fields.Many2one('project.plan.pickings', string="Movimientos de inventario", required=True)
    for_create = fields.Boolean()

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
    
    # @api.constrains('name')
    # def _check_name(self):
    #     for record in self:
    #         if not record.name:
    #             raise ValidationError("El campo 'Name' es obligatorio y no puede estar vacío.")

    # @api.constrains('task_timesheet_id')
    # def _check_task_timesheet_id(self):
    #     for record in self:
    #         if not record.task_timesheet_id:
    #             raise ValidationError("El campo 'Task Timesheet' es obligatorio y no puede estar vacío.")

    # @api.constrains('project_plan_pickings')
    # def _check_project_plan_pickings(self):
    #     for record in self:
    #         if not record.project_plan_pickings:
    #             raise ValidationError("Debe seleccionar al menos un elemento en 'Picking Templates'.")

    # @api.constrains('planned_date_begin', 'planned_date_end')
    # def _check_dates(self):
    #     for record in self:
    #         if record.planned_date_end and record.planned_date_begin:
    #             if record.planned_date_end <= record.planned_date_begin:
    #                 raise ValidationError(
    #                     "La Fecha de finalización no puede ser anterior a la Fecha de inicio."
    #                 )
