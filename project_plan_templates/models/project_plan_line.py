from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

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
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")
    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")
    sale_order_picking_id = fields.Many2one('project.picking.lines', string="Picking")

    
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
    project_plan_pickings = fields.Many2one('project.plan.pickings', string="Lista de materiales")
    for_create = fields.Boolean(default=True)
    for_modification = fields.Boolean(default=True)
    for_picking = fields.Boolean(default=True)
    service_qty = fields.Float(string="Cantidad")
    for_newlines = fields.Boolean(default=True)