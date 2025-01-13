from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError
logger = logging.getLogger(__name__)

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas", readonly=True)
    project_name = fields.Char(string="Nombre del proyecto", required=True)
    user_id = fields.Many2one('res.users', string="Administrador del proyecto")
    description = fields.Html(string="Descripción")
    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Plantilla de movimientos"
    )

    wizard_plan_lines = fields.One2many(
        'project.plan.wizard.line', 'wizard_id',
        string="Project Plan Lines"
    )

    wizard_picking_lines = fields.One2many(
        'project.picking.wizard.line', 'wizard_creation_id',
        string="Project Picking Lines"
    )

    note = fields.Char()

    plan_total_cost = fields.Float(string="Costo total",  compute='_compute_total_cost', default=0.0)

    picking_type_id = fields.Many2one('stock.picking.type', string="Tipo de operacion")
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada de entrega')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    date_start = fields.Datetime(string="Fecha de inicio planeada")
    date = fields.Datetime()
    project_id = fields.Many2one('project.project', string="Proyecto")

    @api.onchange('sale_order_id')
    def _compute_wizard_lines(self):
        for record in self:
            
            record.wizard_picking_lines = [(5, 0, 0)]
            record.wizard_plan_lines = [(5, 0, 0)]

            plan_lines = self.prep_plan_lines(record.sale_order_id.project_plan_lines)
            picking_lines = self.prep_picking_lines(record.sale_order_id.project_picking_lines)

            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines

    
    def action_confirm_create_project(self):
        self.ensure_one()

        if not self.project_id:
            project_vals = {
                'name': self.project_name,
                'description': self.description,
                'project_plan_lines': self.prep_plan_lines(self.wizard_plan_lines),
                'project_picking_lines': self.prep_picking_lines(self.wizard_picking_lines),
                'default_picking_type_id': self.picking_type_id.id,
                'publication_date': fields.Datetime.now(),
                'date_start': self.date_start,
                'date': self.date,
                'sale_order_id': self.sale_order_id.id
            }

            project = self.env['project.project'].create(project_vals)
            logger.warning(f"Id del proyecto: {project.id}")
            self.create_project_tasks(project)

            self.sale_order_id.state = 'sale'
            self.sale_order_id.project_id = project.id

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': project.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            project = self._origin.project_id

            logger.warning(f"Id del sale: {self.sale_order_id.id}")
            
            existing_task_names = project.task_ids.mapped('name')
            curren_task_type = None
            for line in self.wizard_plan_lines:
                if line.display_type and line.for_create:
                    current_task_type = self.get_or_create_task_type(line.name, project)

                if line.use_project_task and not line.display_type and line.for_create:
                    if not current_task_type:
                        current_task_type = self.get_or_create_task_type('Extras', project)
                    if line.name not in existing_task_names and line.use_project_task and line.for_create:
                        timesheet_lines = self.env['task.time.lines'].search([('task_timesheet_id', '=', line.task_timesheet_id.id)])
                        timesheet_data = [(0, 0, {'name': ts_line.description, 'estimated_time': ts_line.estimated_time})
                                        for ts_line in timesheet_lines]

                        picking_lines = []
                        is_task = False

                        for picking in self.wizard_picking_lines:
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
                            'planned_date_begin': line.planned_date_begin,
                            'date_deadline': line.planned_date_end,
                            'project_picking_lines': picking_lines
                        })

                        self.create_project_tasks_pickings(task_id, line.project_plan_pickings.project_picking_lines)

            project.sale_order_id = self.sale_order_id.id

            existing_plan_lines = project.project_plan_lines
            new_plan_lines_data = self.prep_plan_lines(self.wizard_plan_lines)

            project.project_plan_lines = [
                (1, line.id, new_line[2]) if line.name == new_line[2]['name'] else (4, line.id)
                for line in existing_plan_lines
                for new_line in new_plan_lines_data
                if line.name == new_line[2]['name']
            ] + [
                new_line for new_line in new_plan_lines_data
                if all(new_line[2]['name'] != line.name for line in existing_plan_lines)
            ]

            existing_picking_lines = project.project_picking_lines
            new_picking_lines_data = self.prep_picking_lines(self.wizard_picking_lines)

            project.project_picking_lines = [
                (1, line.id, new_line[2]) if line.name == new_line[2]['name'] else (4, line.id)
                for line in existing_picking_lines
                for new_line in new_picking_lines_data
                if line.name == new_line[2]['name']
            ] + [
                new_line for new_line in new_picking_lines_data
                if all(new_line[2]['name'] != line.name for line in existing_picking_lines)
            ]

            self.sale_order_id.state = 'sale'

            return {
                'name': 'Project Version History',
                'view_mode': 'form',
                'res_model': 'project.version.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_project_id': project.id,
                    'default_project_plan_id': project.project_plan_id.id if project.project_plan_id else False,
                    'default_project_plan_lines': [(6, 0, project.project_plan_lines.ids)] if project.project_plan_lines else False,
                    'default_project_picking_lines': [(6, 0, project.project_picking_lines.ids)] if project.project_picking_lines else False,
                    'default_modified_by': self.env.user.id,
                    'default_modification_date': fields.Datetime.now(),
                }
            }

    def get_or_create_task_for_picking(self, picking_line, project):
        # Intentar encontrar una tarea asociada con este picking
        task = self.env['project.task'].search([
            ('project_id', '=', project.id),
            ('name', '=', picking_line.name)  # Asumimos que el nombre del picking puede estar relacionado con el nombre de la tarea
        ], limit=1)

        if not task:
            # Si no se encuentra una tarea, crear una nueva tarea para el picking
            task = self.env['project.task'].create({
                'name': picking_line.name,
                'project_id': project.id,
                'stage_id': self.env.ref('project.project_stage_new').id,  # Usar un stage predeterminado
            })
        
        return task

    def create_project_tasks_pickings(self, task_id, pickings):
        for line in pickings:
            stock_move_vals = [(0, 0, {
                'product_id': line.product_id.id,
                'product_packaging_id': line.product_packaging_id.id,
                'product_uom_qty': line.quantity,
                'quantity': line.quantity,
                'product_uom': line.product_uom.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'name': task_id.name
            })]

            stock_picking_vals = {
                'name': self.env['ir.sequence'].next_by_code('stock.picking') or _('New'),
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
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

    def create_project_tasks(self, project):
        current_task_type = None
        for line in self.wizard_plan_lines:
            if line.display_type and line.for_create:
                current_task_type = self.get_or_create_task_type(line.name, project)

            if line.use_project_task and not line.display_type and line.for_create:
                if not current_task_type:
                    current_task_type = self.get_or_create_task_type('Extras', project)

                timesheet_lines = self.env['task.time.lines'].search([
                    ('task_timesheet_id', '=', line.task_timesheet_id.id)
                ])

                timesheet_data = [(0, 0, {
                    'name': ts_line.description,
                    'estimated_time': ts_line.estimated_time,
                }) for ts_line in timesheet_lines]

                picking_lines = []
                is_task = False

                for picking in self.wizard_picking_lines:
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
                    'planned_date_begin': line.planned_date_begin,
                    'date_deadline': line.planned_date_end,
                    'project_picking_lines': picking_lines
                })

                self.create_project_tasks_pickings(task_id, line.project_plan_pickings.project_picking_lines)

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

    def prep_plan_lines(self, plan):
        plan_lines = []
        for line in plan:
            if line.use_project_task and line.for_create:
                if line.display_type == 'line_section':
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'display_type':  line.display_type or 'line_section',
                        'description': False,
                        'use_project_task': True,
                        'planned_date_begin': False,
                        'planned_date_end': False,
                        'project_plan_pickings': False,
                        'task_timesheet_id': False,
                        'for_create': line.for_create
                    }))
                else:
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'description': line.description,
                        'use_project_task': True,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                        'display_type': False,
                        'for_create': True
                    }))
        return plan_lines

    def prep_picking_lines(self, picking):
        picking_lines = []
        for line in picking:
            if line.display_type == 'line_section':
                picking_lines.append((0, 0, {
                    'name': line.name,
                    'display_type': line.display_type or 'line_section',
                    'product_id': False,
                    'product_uom': False,
                    'product_packaging_id': False,
                    'product_uom_qty': False,
                    'quantity': False,
                    'standard_price': False,
                    'subtotal': False
                }))
            else:
                picking_lines.append((0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_packaging_id': line.product_packaging_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'quantity': line.quantity,
                    'standard_price': line.standard_price,
                    'subtotal': line.subtotal,
                    'display_type': False
                }))
        return picking_lines

    @api.depends('wizard_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.wizard_picking_lines)