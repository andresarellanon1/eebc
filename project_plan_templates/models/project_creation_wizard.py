from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)


class ProjectCreation(models.TransientModel):
    """
    Wizard para confirmar la creación de un proyecto. Este wizard permite configurar los detalles del proyecto,
    incluyendo las líneas de planificación y los movimientos de inventario asociados.
    """

    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    # Campos del wizard
    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas", readonly=True)
    project_name = fields.Char(string="Nombre del proyecto", required=True)
    user_id = fields.Many2one('res.users', string="Administrador del proyecto")
    description = fields.Html(string="Descripción")
    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    
    # Relaciones con plantillas de movimientos y líneas de planificación
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Plantilla de movimientos"
    )

    wizard_plan_lines = fields.One2many(
        'project.plan.wizard.line', 
        'wizard_id',
        string="Líneas de planificación del proyecto"
    )

    wizard_picking_lines = fields.One2many(
        'project.picking.wizard.line',  
        'wizard_creation_id',  
        string="Líneas de picking del proyecto"
    )

    note = fields.Char()

    # Campos para costos y detalles de inventario
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)
    picking_type_id = fields.Many2one('stock.picking.type', string="Tipo de operación")
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada de entrega')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    date_start = fields.Datetime(string="Fecha de inicio planeada")
    date = fields.Datetime()
    project_id = fields.Many2one('project.project', string="Proyecto")
    client_id = fields.Many2one('res.partner', string='Cliente')

    @api.onchange('sale_order_id')
    def _compute_wizard_lines(self):
        """
        Prepara las líneas de planificación y picking del proyecto cuando se abre el wizard.
        """
        for record in self:
            # Limpiar líneas existentes
            record.wizard_picking_lines = [(5, 0, 0)]
            record.wizard_plan_lines = [(5, 0, 0)]

            # Preparar nuevas líneas de planificación y picking
            plan_lines = self.prep_plan_lines(record.sale_order_id.project_plan_lines)
            picking_lines = self.prep_picking_lines(record.sale_order_id.project_picking_lines)

            # Asignar las líneas preparadas
            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines
    
    def action_confirm_create_project(self):
        """
        Crea el proyecto con la información generada en el presupuesto del proyecto.
        """
        self.ensure_one()

        # Validar si hay líneas de planificación
        for line in self.wizard_plan_lines:
            logger.info("No hay datos en Wizard Plan Line")

        # Cambiar el estado de la orden de venta a 'venta'
        self.sale_order_id.state = 'sale'

        # Preparar los valores para crear el proyecto
        project_vals = {
            'name': self.project_name,
            'description': self.description,
            'project_plan_lines': self.prep_plan_lines(self.wizard_plan_lines),
            'project_picking_lines': self.prep_picking_lines(self.wizard_picking_lines),
            'default_picking_type_id': self.picking_type_id.id,
            'publication_date': fields.Datetime.now(),
            'date_start': self.date_start,
            'date': self.date,
            'actual_sale_order_id': self.sale_order_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id
        }

        # Crear el proyecto
        project = self.env['project.project'].create(project_vals)
        logger.warning(f"Id del proyecto: {project.id}")

        # Crear las tareas del proyecto
        self.create_project_tasks(project)

        # Registrar el historial de versiones del proyecto
        existing_history = self.env['project.version.history'].search([
            ('project_id', '=', project.id), 
            ('client_id', '=', self.project_id.client_id.id)
        ], limit=1)

        if not existing_history:
            history = self.env['project.version.history'].create({
                'project_id': project.id,
                'modified_by': self.env.user.id,
                'modification_motive': 'Se ha creado el proyecto',
                'project_name': project.name,
                'client_id': project.client_id.id,
            })

        # Limpiar las líneas de picking modificadas
        for sale in self.sale_order_id.project_picking_lines:
            sale.for_modification = False

        # Marcar las líneas como creadas
        self.sale_order_id.project_lines_created()

        # Registrar las líneas de planificación y picking en el historial
        self.env['project.version.lines'].create({
            'project_version_history_id': history.id,
            'modification_date': fields.Datetime.now(),
            'modified_by': self.env.user.id,
            'modification_motive': 'Se ha creado el proyecto',
            'project_plan_lines': [(6, 0, self.sale_order_id.project_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.sale_order_id.project_picking_lines.ids)],
        })

        # Asignar el proyecto a la orden de venta
        self.sale_order_id.project_id = project.id

        # Abrir la vista del proyecto recién creado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def get_or_create_task_for_picking(self, picking_line, project):
        """
        Obtiene o crea una tarea asociada con un movimiento de inventario.
        
        :param picking_line: Línea de picking.
        :param project: Proyecto asociado.
        :return: Tarea existente o recién creada.
        """
        task = self.env['project.task'].search([
            ('project_id', '=', project.id),
            ('name', '=', picking_line.name)
        ], limit=1)

        if not task:
            task = self.env['project.task'].create({
                'name': picking_line.name,
                'project_id': project.id,
                'stage_id': self.env.ref('project.project_stage_new').id,
            })
        
        return task

    def create_project_tasks_pickings(self, task_id, pickings):
        """
        Crea los movimientos de inventario asociados a una tarea.
        
        :param task_id: Tarea asociada.
        :param pickings: Líneas de picking.
        """
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
        """
        Genera las tareas del proyecto con los servicios presupuestados.
        
        :param project: Proyecto asociado.
        """
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
                    'work_shift': ts_line.work_shift * line.service_qty
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
                    'description': line.description,
                    'planned_date_begin': line.planned_date_begin,
                    'date_deadline': line.planned_date_end,
                    'project_picking_lines': picking_lines
                })

                self.create_project_tasks_pickings(task_id, picking_lines)

    def get_or_create_task_type(self, stage_id, project):
        """
        Obtiene o crea un tipo de tarea para el proyecto.
        
        :param stage_id: Nombre del tipo de tarea.
        :param project: Proyecto asociado.
        :return: Tipo de tarea existente o recién creado.
        """
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
        """
        Prepara las líneas de planificación para su uso en el proyecto.
        
        :param plan: Líneas de planificación.
        :return: Lista de líneas de planificación preparadas.
        """
        plan_lines = []
        for line in plan:
            if line.use_project_task:
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
                        'for_create': line.for_create,
                        'for_modification': line.for_modification,
                        'for_newlines': line.for_newlines,
                        'service_qty': line.service_qty
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
                        'for_create': True,
                        'for_modification': line.for_modification,
                        'for_newlines': line.for_newlines,
                        'service_qty': line.service_qty
                    }))
        return plan_lines

    def prep_picking_lines(self, picking):
        """
        Prepara las líneas de picking para su uso en el proyecto.
        
        :param picking: Líneas de picking.
        :return: Lista de líneas de picking preparadas.
        """
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
                    'subtotal': False,
                    'for_modification': line.for_modification,
                    'for_newlines': line.for_newlines,
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
                    'display_type': False,
                    'for_modification': line.for_modification,
                    'for_newlines': line.for_newlines,
                }))
        return picking_lines

    @api.depends('wizard_picking_lines.subtotal')
    def _compute_total_cost(self):
        """
        Calcula el costo total de los materiales basado en las líneas de picking.
        """
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.wizard_picking_lines)