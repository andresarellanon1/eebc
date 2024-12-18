from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProjecVersionLines(models.Model):
    _name = 'project.version.lines'
    _description = 'Project versions history'

    modification_date = fields.Datetime(string='Fecha de modificación')
    project_id = fields.Many2one('project.project', string='Proyecto')
    modified_by = fields.Many2one('res.users', string='Modificado por')
    modification_motive = fields.Html(string='Motivo de los cambios')
    project_name = fields.Char(string='Nombre del proyecto')
    project_version_history_id = fields.Many2one('project.version.history', string="Historial del proyecto")
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación',
        relation='project_version_lines_project_plan_line_rel'
    )

    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Inventario',
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
        string='Numero de versión',
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
                record.previous_version_plan_lines = [(5, 0, 0)]
                record.previous_version_plan_lines = [
                    (0, 0, {
                        'name': line.name,
                        'description': line.description,
                        'use_project_task': line.use_project_task,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'partner_id': line.partner_id.id,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                    })
                    for line in previous_version.project_plan_lines
                ]

                aux_previous_project_plan_lines =  record.previous_version_plan_lines

                previous_version.project_plan_lines = [(5, 0, 0)]
                previous_version.project_plan_lines = [
                    (0, 0, {
                        'name': line.name,
                        'description': line.description,
                        'use_project_task': line.use_project_task,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'partner_id': line.partner_id.id,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                    })
                    for line in aux_previous_project_plan_lines
                ]

                aux_project_plan_lines =  record.project_plan_lines

                record.project_plan_lines = [(5, 0, 0)]
                record.project_plan_lines = [
                    (0, 0, {
                        'name': line.name,
                        'description': line.description,
                        'use_project_task': line.use_project_task,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'partner_id': line.partner_id.id,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                    })
                    for line in aux_project_plan_lines
                ]

              
                
                record.previous_version_picking_lines = [(5, 0, 0)]
                record.previous_version_picking_lines = [
                    (0, 0, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'product_packaging_id': line.product_packaging_id.id,
                        'quantity': line.quantity,
                        'reservado': line.reservado,
                        'standard_price': line.standard_price,
                        'subtotal': line.subtotal,
                    })
                    for line in previous_version.project_picking_lines
                ]

                aux_previous_project_pickings_lines =  record.previous_version_picking_lines
                previous_version.project_picking_lines = [(5, 0, 0)]
                previous_version.project_picking_lines = [
                    (0, 0, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'product_packaging_id': line.product_packaging_id.id,
                        'quantity': line.quantity,
                        'reservado': line.reservado,
                        'standard_price': line.standard_price,
                        'subtotal': line.subtotal,
                    })
                    for line in aux_previous_project_pickings_lines
                ]

                aux_project_picking_lines =  record.project_picking_lines
                record.project_picking_lines = [(5, 0, 0)]
                record.project_picking_lines = [
                    (0, 0, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'product_packaging_id': line.product_packaging_id.id,
                        'quantity': line.quantity,
                        'reservado': line.reservado,
                        'standard_price': line.standard_price,
                        'subtotal': line.subtotal,
                    })
                    for line in aux_project_picking_lines
                ]

            else:
                _logger.warning('No tiene version previa')
                record.previous_version_plan_lines = [(5, 0, 0)]
                record.previous_version_picking_lines = [(5, 0, 0)]
