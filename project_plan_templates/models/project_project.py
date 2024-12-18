from odoo import fields, api, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas", readonly="True")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Movimientos de inventario")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines", compute="_compute_picking_lines", store=True)
    plan_total_cost = fields.Float(string="Costo total", default=0.0)

    def create_project_tasks(self):
        for project in self:
            for line in project.project_plan_lines:
                if line.display_type:
                    current_task_type = self.get_or_create_task_type(line.name, project)

                if line.use_project_task and not line.display_type:
                    if not current_task_type:
                        current_task_type = self.get_or_create_task_type('Extras', project)

                    existing_task = self.env['project.task'].search([
                        ('name', '=', line.name),
                        ('project_id', '=', project.id)
                    ], limit=1)

                    if not existing_task:
                        timesheet_lines = self.env['task.time.lines'].search([
                            ('task_timesheet_id', '=', line.task_timesheet_id.id)
                        ])

                        timesheet_data = [(0, 0, {
                            'name': ts_line.description,
                            'estimated_time': ts_line.estimated_time,
                        }) for ts_line in timesheet_lines]

                        self.env['project.task'].create({
                            'name': line.name,
                            'project_id': project.id,
                            'description': line.description,
                            'planned_date_begin': line.planned_date_begin,
                            'date_deadline': line.planned_date_end,
                            'user_ids': [(6, 0, line.partner_id.ids)],
                            'timesheet_ids': timesheet_data,
                        })
                    else:
                        existing_task.name = line.name
                        existing_task.description = line.description
                        existing_task.planned_date_begin = line.planned_date_begin
                        existing_task.date_deadline = line.planned_date_end
                        existing_task.user_ids = [(6, 0, line.partner_id.ids)]

                        if not existing_task.timesheet_ids and line.task_timesheet_id:
                            timesheet_lines = self.env['task.time.lines'].search([
                                ('task_timesheet_id', '=', line.task_timesheet_id.id)
                            ])

                            timesheet_data = [(0, 0, {
                                'name': ts_line.description,
                                'estimated_time': ts_line.estimated_time,
                            }) for ts_line in timesheet_lines]

                            existing_task.timesheet_ids = timesheet_data

    @api.depends('project_plan_lines')
    def _compute_picking_lines(self):
        for record in self:
            record.project_picking_lines = [(5, 0, 0)]
            record.project_picking_lines = record.sale_order_id.get_picking_lines(record.project_plan_lines)
            for line in record.project_plan_lines:
                _logger.warning(line.id)
                _logger.warning(line.sequence)

    def get_or_create_task_type(self, stage_id, project):
        task_type = self.env['project.task.type'].search([
            ('name', '=', stage_id),
            ('project_ids', 'in', project.id)
        ], limit=1)

        if not task_type:
            task_type = self.env['project.task.type'].create({
                'name': stage_id,
                'project_ids': [(4, project.id)],
            })

        return task_type