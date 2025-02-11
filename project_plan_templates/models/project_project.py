from odoo import fields, api, models
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas", readonly=True)
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines", compute="_compute_project_plan_lines", store=True)
    
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Movimientos de inventario")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines", compute="_compute_project_picking_lines", store=True)
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)
    sale_order_id = fields.Many2one('sale.order', string='Orden de venta', readonly=False, store=True)
    actual_sale_order_id = fields.Many2one('sale.order', string="Orden actual de venta", store=True)

    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada de entrega')
    contact_id = fields.Many2one('res.partner', string='Contacto')
    date_start = fields.Datetime(string="Fecha de inicio planeada")
    client_id = fields.Many2one('res.partner', string="Cliente")

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.depends('sale_order_id')
    def _compute_project_picking_lines(self):
        for record in self:
            record.project_picking_lines = [(5, 0, 0)]

            record.project_picking_lines = self.prep_picking_lines(self.sale_order_id.project_picking_lines)

    @api.depends('sale_order_id')
    def _compute_project_plan_lines(self):
        for record in self:
            record.project_plan_lines = [(5, 0, 0)]

            record.project_plan_lines = self.prep_plan_lines(self.sale_order_id.project_plan_lines)

    def prep_picking_lines(self, picking):
        picking_lines = []
        for line in picking:
            if line.display_type == 'line_section':
                picking_lines.append((0, 0, {
                    'name': line.name,
                    'sequence': line.sequence,
                    'display_type': line.display_type or 'line_section',
                    'product_id': False,
                    'product_uom': False,
                    'product_packaging_id': False,
                    'product_uom_qty': False,
                    'quantity': False,
                    'standard_price': False,
                    'subtotal': False,
                    'for_newlines': line.for_newlines,
                    'for_modification': line.for_modification
                }))
            else:
                picking_lines.append((0, 0, {
                    'name': line.product_id.name,
                    'sequence': line.sequence,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_packaging_id': line.product_packaging_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'quantity': line.quantity,
                    'standard_price': line.standard_price,
                    'subtotal': line.subtotal,
                    'display_type': False,
                    'for_newlines': line.for_newlines,
                    'for_modification': line.for_modification
                }))
        return picking_lines

    def prep_plan_lines(self, plan):
        plan_lines = []
        for line in plan:
            if line.use_project_task:
                if line.display_type == 'line_section':
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'sequence': line.sequence,
                        'display_type':  line.display_type or 'line_section',
                        'description': False,
                        'use_project_task': True,
                        'planned_date_begin': False,
                        'planned_date_end': False,
                        'project_plan_pickings': False,
                        'task_timesheet_id': False,
                        'for_create': line.for_create,
                        'for_newlines': line.for_newlines,
                        'service_qty': line.service_qty,
                        'for_modification': line.for_modification
                    }))
                else:
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'sequence': line.sequence,
                        'description': line.description,
                        'use_project_task': True,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                        'display_type': False,
                        'for_create': True,
                        'for_newlines': line.for_newlines,
                        'service_qty': line.service_qty,
                        'for_modification': line.for_modification
                    }))
        return plan_lines

    def create_project_tasks(self, location_id, location_dest_id, scheduled_date):
        for project in self:
            current_task_type = None

            for line in project.project_plan_lines:
                if line.display_type and line.for_create:
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
                            'work_shift': ts_line.work_shift * line.service_qty
                        }) for ts_line in timesheet_lines]

                        picking_lines = []
                        is_task = False

                        for picking in project.project_picking_lines:
                            if picking.display_type:
                                is_task = picking.name == line.name
                            elif is_task and picking.for_newlines:
                                picking_lines.append((0, 0, {
                                    'name': picking.product_id.name,
                                    'product_id': picking.product_id.id,
                                    'product_uom': picking.product_uom.id,
                                    'product_packaging_id': picking.product_packaging_id.id,
                                    'product_uom_qty': picking.product_uom_qty,
                                    'quantity': picking.quantity,
                                    'standard_price': picking.standard_price,
                                    'subtotal': picking.subtotal,
                                    'display_type': False,
                                    'for_modification': False,
                                    'for_newlines': False,
                                    'for_create': False
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

                        self.create_project_tasks_pickings(task_id, picking_lines, location_id, location_dest_id, scheduled_date)
                    else:
                        existing_task.write({
                            'name': line.name,
                            'description': line.description,
                            'planned_date_begin': line.planned_date_begin,
                            'date_deadline': line.planned_date_end,
                            'user_ids': [(6, 0, line.partner_id.ids)]
                        })

                        if not existing_task.timesheet_ids and line.task_timesheet_id:
                            timesheet_lines = self.env['task.time.lines'].search([
                                ('task_timesheet_id', '=', line.task_timesheet_id.id)
                            ])

                            timesheet_data = [(0, 0, {
                                'name': ts_line.description,
                                'work_shift': ts_line.work_shift * line.service_qty,
                                'estimated_time': ts_line.estimated_time,
                            }) for ts_line in timesheet_lines]

                            existing_task.timesheet_ids = timesheet_data

                        picking_lines = []
                        is_task = False

                        for picking in project.project_picking_lines:
                            if picking.display_type:
                                is_task = picking.name == line.name
                            elif is_task and picking.for_newlines:
                                picking_lines.append((0, 0, {
                                    'name': picking.product_id.name,
                                    'product_id': picking.product_id.id,
                                    'product_uom': picking.product_uom.id,
                                    'product_packaging_id': picking.product_packaging_id.id,
                                    'product_uom_qty': picking.product_uom_qty,
                                    'quantity': picking.quantity,
                                    'standard_price': picking.standard_price,
                                    'subtotal': picking.subtotal,
                                    'display_type': False,
                                    'for_modification': False,
                                    'for_newlines': False,
                                    'for_create': False
                                }))

                        if picking_lines:
                            existing_task.project_picking_lines = [(4, picking.id) for picking in existing_task.project_picking_lines] + picking_lines

                        self.create_project_tasks_pickings(existing_task, picking_lines, location_id, location_dest_id, scheduled_date)

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

    def create_project_tasks_pickings(self, task_id, pickings, location_id, location_dest_id, scheduled_date):
        for line in pickings:
            line_data = line[2] if isinstance(line, tuple) else line  # Acceder al diccionario

            stock_move_vals = [(0, 0, {
                'product_id': line_data['product_id'],
                'product_packaging_id': line_data['product_packaging_id'],
                'product_uom_qty': line_data['quantity'],
                'quantity': line_data['quantity'],
                'product_uom': line_data['product_uom'],
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'name': task_id.name
            })]

            stock_picking_vals = {
                'name': self.env['ir.sequence'].next_by_code('stock.picking') or _('New'),
                'partner_id': self.contact_id.id,
                'picking_type_id': self.default_picking_type_id.id,
                'location_id': location_id,
                'scheduled_date': scheduled_date,
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