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
    sale_order_id = fields.Many2one('sale.order', string='Orden de venta', readonly=False, store=True)
    actual_sale_order_id = fields.Many2one('sale.order', string="Orden de venta", store=True)

    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada de entrega')
    contact_id = fields.Many2one('res.partner', string='Contacto')
    date_start = fields.Datetime(string="Fecha de inicio planeada")

    def create_project_tasks(self, picking_type):
        for project in self:

            current_task_type = None

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

                        picking_lines = []
                        is_task = False

                        for picking in self.project_picking_lines:
                            if picking.display_type:
                                is_task = picking.name == line.name
                            elif is_task:
                                picking_lines.append((0, 0, {
                                    'name': picking.product_id.name,
                                    'product_id': picking.product_id.id,
                                    'product_uom': picking.product_uom.id,
                                    'product_packaging_id': picking.product_packaging_id.id,
                                    'product_uom_qty': picking.product_uom_qty,
                                    'quantity': picking.quantity,
                                    'standard_price': picking.standard_price,
                                    'subtotal': picking.subtotal,
                                    'display_type': False
                                }))

                        task_id = self.env['project.task'].create({
                            'name': line.name,
                            'project_id': project.id,
                            'stage_id': current_task_type.id,
                            'timesheet_ids': timesheet_data,
                            'description': line.description,
                            'planned_date_begin': line.planned_date_begin,
                            'date_deadline': line.planned_date_end,
                            'project_picking_lines': picking_lines
                        })

                        self.create_project_tasks_pickings(task_id, picking_lines, picking_type)
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

    def create_project_tasks_pickings(self, task_id, pickings, picking_type):
        for line in pickings:
            line_data = line[2] if isinstance(line, tuple) else line  # Acceder al diccionario

            stock_move_vals = [(0, 0, {
                'product_id': line_data['product_id'],
                'product_packaging_id': line_data['product_packaging_id'],
                'product_uom_qty': line_data['quantity'],
                'quantity': line_data['quantity'],
                'product_uom': line_data['product_uom'],
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'name': task_id.name
            })]

            stock_picking_vals = {
                'name': self.env['ir.sequence'].next_by_code('stock.picking') or _('New'),
                'partner_id': self.contact_id.id,
                'picking_type_id': picking_type,
                'location_id': self.location_id.id,
                'scheduled_date': self.scheduled_date,
                'origin': task_id.name,
                'task_id': task_id.id,
                'user_id': self.env.user.id,
                'move_ids': stock_move_vals,
                'carrier_id': False,
                'carrier_tracking_ref': False,
                'weight': False,
                'shipping_weight': False,
                'company_id': self.env.company.id,
                'transport_type': False,
                'custom_document_identification': False,
                'lat_origin': False,
                'long_origin': False,
                'lat_dest': False,
                'long_dest': False,
                'note': False,
                'state': 'draft'
            }

            self.env['stock.picking'].create(stock_picking_vals)