from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProjecVersionLines(models.Model):
    _name = 'project.version.lines'
    _description = 'Project versions history'

    modification_date = fields.Datetime(string='Modification date')
    project_id = fields.Many2one('project.project', string='Project')
    modified_by = fields.Many2one('res.users', string='Modified by')
    modification_motive = fields.Html(string='Motive of adjustment')
    project_name = fields.Char(string='Project name')
    project_version_history_id = fields.Many2one('project.version.history', string="Project history")
    plan_total_cost = fields.Float(string="Total cost", compute='_compute_total_cost', default=0.0)

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación',
        relation='project_version_lines_project_plan_line_rel'
    )

    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock',
        relation='project_version_lines_picking_lines_rel'
    )

    previous_version_plan_lines = fields.Many2many(
        'project.plan.line',
        string="Last version plan lines",
        relation='project_version_lines_previous_plan_line_rel'
    )

    previous_version_picking_lines = fields.Many2many(
        'project.picking.lines',
        string="Last version picking lines",
        relation='project_version_lines_previous_picking_lines_rel'
    )

    version_number = fields.Char(
        string='Version Number',
        compute='_compute_version_number',
        store=True
    )

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    has_previous_version = fields.Boolean(
        string="Has Previous Version",
        compute='_compute_previous_version_lines',
        store=True
    )

    @api.depends('modification_date', 'project_id')
    def _compute_version_number(self):
        for record in self:
            if record.project_id:
                versions = self.env['project.version.lines'].search(
                    [('project_id', '=', record.project_id.id)],
                    order='modification_date'
                )
                record.version_number = f"V{versions.ids.index(record.id) + 1}" if record.id else "V0"
            else:
                record.version_number = "V0"

    @api.depends('project_id')
    def _compute_previous_version_lines(self):
        for record in self:
            record.project_name = record.project_id.name
            _logger.warning(f"Buscando versiones previas para record ID {record.id}, project_id {record.project_id.id}")

            previous_version = self.search([
                ('project_id', '=', record.project_id.id),
                ('id', '<', record.id)
            ], order="id desc", limit=1)
            _logger.warning(f"Resultado de búsqueda: {previous_version}")
            
            if previous_version:
                record.previous_version_plan_lines = previous_version.project_plan_lines
                _logger.warning(f'La version previa es: {previous_version.project_plan_lines}')
                record.previous_version_picking_lines = previous_version.project_picking_lines
                record.has_previous_version = True
            else:
                _logger.warning('No tiene version previa')
                record.previous_version_plan_lines = [(5, 0, 0)]
                record.previous_version_picking_lines = [(5, 0, 0)]
