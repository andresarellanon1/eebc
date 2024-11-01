from odoo import fields, api, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Project template", readonly="True")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines")

    def action_create_tasks(self):
        for project in self:
            for line in project.project_plan_lines:
                _logger.warning('Contenido de line: %s', line.read())
                
                stage = project.env['project.task.type'].search([('name', '=', line.stage_id)], limit=1)
                stage_id = stage.id if stage else False

                project.env['project.task'].create({
                    'name': line.name,
                    'project_id': project.id,
                    'chapter': line.chapter,
                    'description': line.description,
                    'product_uom': line.product_uom,
                    'unit_price': line.unit_price,
                    'amount_total': line.amount_total,
                    'use_project_task': line.use_project_task,
                    'stage_id': stage_id,
                    'planned_date_begin': line.planned_date_begin,
                    'planned_date_end': line.planned_date_end,
                    'origin_project_id': line.origin_project_id,
                    'partner_id': line.partner_id,
                    'task_timesheet_id': line.task_timesheet_id,
                })

