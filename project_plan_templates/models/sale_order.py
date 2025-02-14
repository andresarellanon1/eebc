from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """
    Modelo que hereda de 'sale.order' para agregar funcionalidades relacionadas con proyectos.
    """

    _inherit = 'sale.order'

    # Campos adicionales para manejar proyectos
    is_project = fields.Boolean(string="Es proyecto?", default=False)
    project_name = fields.Char(string="Titulo de proyecto")
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    # Extensión del campo 'state' para incluir estados adicionales relacionados con proyectos
    state = fields.Selection(
        selection_add=[
            ('budget', 'Presupuesto'),
            ('process', 'En proceso'),
        ],
        ondelete={'budget': 'set default', 'process': 'set default'},
    )

    # Relaciones con otros modelos
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")
    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')
    project_id = fields.Many2one('project.project', string="Proyecto")
    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id')
    edit_project = fields.Boolean(string="Modificar proyecto", default=False)

    # Campo calculado para determinar si el pedido es editable
    is_editable = fields.Boolean(
        string='Editable',
        compute='_compute_is_editable',
        store=True
    )

    # Líneas de mano de obra relacionadas con el proyecto
    task_time_lines = fields.One2many(
        'task.time.lines',
        'sale_order_id',
        string="Lineas de mano obra")

    # Costo total de la mano de obra
    labour_total_cost = fields.Float(string="Costo mano de obra", compute="_compute_labour_cost", default=0.0)

    def update_task_lines(self):
        """
        Actualiza las líneas de tareas basadas en las líneas de planificación del proyecto.
        """
        for record in self:
            record.task_time_lines = record.get_task_time_lines(record.project_plan_lines)

    def get_task_time_lines(self, line):
        """
        Genera las líneas de tareas a partir de las líneas de planificación.
        
        :param line: Líneas de planificación del proyecto.
        :return: Lista de líneas de tareas.
        """
        task_lines = []
        for task in line:
            if task.for_modification:
                if task.display_type == 'line_section':
                    task_lines.append(self.prep_task_line_section_line(task))
                else:
                    task_lines += self.prep_task_time_lines(task)
            task.for_modification = False
        return task_lines

    def prep_task_time_lines(self, line):
        """
        Prepara las líneas de tareas individuales.
        
        :param line: Línea de planificación.
        :return: Lista de líneas de tareas.
        """
        task_lines = []
        for task in line.task_timesheet_id.task_time_lines:
            task_lines.append((0, 0, {
                'product_id': task.product_id.id,
                'description': task.description,
                'estimated_time': task.estimated_time,
                'work_shift': task.work_shift * line.service_qty,
                'unit_price': task.unit_price,
                'price_subtotal': task.price_subtotal
            }))
        return task_lines

    @api.depends('task_time_lines.price_subtotal')
    def _compute_labour_cost(self):
        """
        Calcula el costo total de la mano de obra basado en las líneas de tareas.
        """
        for task in self:
            task.labour_total_cost = sum(line.price_subtotal for line in task.task_time_lines)

    @api.depends('state')
    def _compute_is_editable(self):
        """
        Determina si el pedido es editable según su estado.
        """
        for sale in self:
            sale.is_editable = sale.state in ['draft', 'budget']

    def update_picking_lines(self):
        """
        Actualiza las líneas de picking basadas en las líneas de planificación del proyecto.
        """
        for record in self:
            existing_lines = {line.name: line.sequence for line in record.project_picking_lines}
            picking_lines = record.get_picking_lines(record.project_plan_lines)
            for line in picking_lines:
                line_name = line[2].get('name', '')
                if line_name in existing_lines:
                    line[2]['sequence'] = existing_lines[line_name]
            record.project_picking_lines = sorted(picking_lines, key=lambda x: x[2]['sequence'])

    def get_picking_lines(self, line):
        """
        Genera las líneas de picking a partir de las líneas de planificación.
        
        :param line: Líneas de planificación del proyecto.
        :return: Lista de líneas de picking.
        """
        picking_lines = []
        for picking in line:
            if picking.for_picking:
                if picking.for_create:
                    if picking.display_type == 'line_section':
                        picking_lines.append(self.prep_picking_section_line(picking, True, False))
                    else:
                        picking_lines += self.prep_picking_lines(picking)
                else:
                    picking_lines.append(self.prep_picking_section_line(picking, False, True))
                picking.for_picking = False
        return picking_lines
    
    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        """
        Calcula el costo total del proyecto basado en las líneas de picking.
        """
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.onchange('is_project')
    def _onchange_is_project(self):
        """
        Maneja el cambio en el campo 'is_project'. Limpia las líneas de la orden si no es un proyecto.
        """
        for record in self:
            record.order_line = None
            if not record.is_project and record.edit_project:
                record.edit_project = False
                record.project_id = False

    def action_generate_planning(self):
        """
        Genera las líneas de planificación, materiales y mano de obra del proyecto.
        """
        self.ensure_one()
        for sale in self:
            if sale.is_project:
                if not sale.project_name and not sale.edit_project:
                    raise ValidationError(
                        f"se requiere el nombre del proyecto"
                    ) 
                
                """
                Elimina las lineas que ya han sido modificadas para reemplazarlas
                """
                # plannig_lines_to_remove = sale.project_plan_lines.filtered(lambda line: not line.for_modification)
                # plannig_lines_to_remove.unlink()
                # time_lines_to_remove = sale.task_time_lines.filtered(lambda line: not line.for_modification)
                # time_lines_to_remove.unlink()
                # picking_lines_to_remove = sale.project_picking_lines.filtered(lambda line: not line.for_modification)
                # picking_lines_to_remove.unlink() 

                sale.project_plan_lines.unlink()
                sale.project_picking_lines.unlink()
                sale.task_time_lines.unlink()

                plan_pickings = []
                existing_lines = {line.name: line.sequence for line in sale.project_plan_lines}
                plan_lines = []
                for line in sale.order_line:
                    # if line.for_modification:
                        if line.display_type == 'line_section':
                            plan_lines.append(self.prep_plan_section_line(line, True, False, True))
                        else:
                            if line.product_id.project_plan_id:
                                plan_lines.append(self.prep_plan_section_line(line, False, True, False))
                                plan_lines += self.prep_plan_lines(line)
                            for project_picking in line.product_id.project_plan_id.project_plan_pickings:
                                plan_pickings.append((4, project_picking.id))
                        line.for_modification = False
                        line.is_modificated = True
                    
                for plan in plan_lines:
                    plan_name = plan[2].get('name', '')
                    if plan_name in existing_lines:
                        plan[2]['sequence'] = existing_lines[plan_name]

                sale.project_plan_pickings = plan_pickings
                sale.project_plan_lines = sorted(plan_lines, key=lambda x: x[2]['sequence'])
                sale.update_picking_lines()
                sale.update_task_lines()

            self.change_for_modification()
            sale.state = 'budget'
    
    def change_for_modification(self):
        """
        Limpia el campo 'for_modification' en las líneas de picking.
        """
        for sale in self.project_picking_lines:
            sale.for_modification = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """
        Obtiene la información de la orden de venta anterior al modificar un proyecto en proceso.
        """
        for sale in self:
            if sale.project_id:
                # Asignar cliente desde el proyecto
                sale.partner_id = sale.project_id.client_id  

                # Limpiar líneas previas para evitar duplicados
                sale.order_line = [(5, 0, 0)]
                sale.project_plan_lines = [(5, 0, 0)]
                sale.project_picking_lines = [(5, 0, 0)]
                sale.task_time_lines = [(5, 0, 0)]

                # Si el proyecto tiene un pedido anterior, copiamos datos
                if sale.edit_project and sale.project_id.actual_sale_order_id:
                    previous_order = sale.project_id.actual_sale_order_id

                    # Copiar líneas del pedido anterior
                    sale.order_line = [(0, 0, {
                        'product_id': line.product_id.id,
                        'display_type': line.display_type,
                        'name': line.name,
                        'product_uom_qty': 0,
                        'price_unit': line.last_service_price,
                        'discount': line.discount,
                        'for_modification': False,
                        'last_service_price': line.last_service_price,
                        'product_pricelist_id': line.product_pricelist_id,
                    }) for line in previous_order.order_line]

                    # Copiar líneas de plan
                    sale.project_plan_lines = self._prepare_plan_lines(previous_order.project_plan_lines)

                    # Copiar líneas de picking
                    sale.project_picking_lines = self._prepare_picking_lines(previous_order.project_picking_lines)

                    # Copiar líneas de tareas
                    sale.task_time_lines = self._prepare_task_lines(previous_order.task_time_lines)

                    _logger.warning(f"Se copiaron {len(previous_order.order_line)} líneas de orden al nuevo pedido")

                    for plan_line in sale.order_line:
                        _logger.warning(f"Plan Line: {plan_line} | Nombre: {plan_line.name} | price_unit: {plan_line.price_unit} | last_service_price: {plan_line.last_service_price}")
                
    
    def _prepare_task_lines(self, lines):
        """
        Prepara las líneas de mano de obra para su reutilización en la modificación de proyectos.
        
        :param lines: Líneas de mano de obra existentes.
        :return: Lista de líneas de mano de obra preparadas.
        """
        return [(0, 0, {
            'name': line.name,
            'display_type': line.display_type,
            'product_id': line.product_id.id,
            'description': line.description,
            'estimated_time': line.estimated_time,
            'work_shift': line.work_shift,
            'unit_price': line.unit_price,
            'price_subtotal': line.price_subtotal,
            'for_modification': False,
            'not_modificable': line.not_modificable
        }) for line in lines]

    def _prepare_plan_lines(self, lines):
        """
        Prepara las líneas de planificación para su reutilización en la modificación de proyectos.
        
        :param lines: Líneas de planificación existentes.
        :return: Lista de líneas de planificación preparadas.
        """
        return [(0, 0, {
            'name': line.name,
            'sequence': line.sequence,
            'display_type': line.display_type,
            'description': line.description,
            'use_project_task': line.use_project_task,
            'planned_date_begin': line.planned_date_begin,
            'planned_date_end': line.planned_date_end,
            'project_plan_pickings': line.project_plan_pickings.id if line.project_plan_pickings else False,
            'task_timesheet_id': line.task_timesheet_id.id if line.task_timesheet_id else False,
            'for_create': line.for_create,
            'for_modification': False,
            'for_picking': line.for_picking,
            'for_newlines': line.for_newlines,
            'not_modificable': line.not_modificable
        }) for line in lines]

    def _prepare_picking_lines(self, lines):
        """
        Prepara las líneas de picking para su reutilización en la modificación de proyectos.
        
        :param lines: Líneas de picking existentes.
        :return: Lista de líneas de picking preparadas.
        """
        return [(0, 0, {
            'name': line.name,
            'sequence': line.sequence,
            'display_type': line.display_type,
            'product_id': line.product_id.id if line.product_id else False,
            'product_uom': line.product_uom.id if line.product_uom else False,
            'product_packaging_id': line.product_packaging_id.id if line.product_packaging_id else False,
            'product_uom_qty': line.product_uom_qty,
            'quantity': line.quantity,
            'standard_price': line.last_price,
            'subtotal': line.subtotal,
            'for_create': line.for_create,
            'for_modification': False,
            'last_price': line.last_price,
            'for_newlines': line.for_newlines,
            'not_modificable': line.not_modificable
        }) for line in lines]

    def prep_task_line_section_line(self, line):
        """
        Prepara una línea de sección para las líneas de mano de obra.
        
        :param line: Línea de planificación.
        :return: Línea de sección preparada.
        """
        return(0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'product_id':  False,
            'description':  False,
            'estimated_time':  False,
            'work_shift':  False,
            'unit_price':  False,
            'price_subtotal': False,
            'not_modificable': False
        })
    
    def prep_picking_section_line(self, line, for_create, for_task):
        """
        Prepara una línea de sección para las líneas de picking.
        
        :param line: Línea de planificación.
        :param for_create: Indica si la línea es para creación.
        :param for_task: Indica si la línea es para tareas.
        :return: Línea de sección preparada.
        """
        return (0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'product_id': False,
            'sequence': 0,
            'product_uom': False,
            'product_packaging_id': False,
            'product_uom_qty': False,
            'quantity': False,
            'standard_price': False,
            'subtotal': False,
            'for_create': for_create,
            'for_modification': False,
            'last_price': False,
            'not_modificable': False
        })
    
    def prep_plan_section_line(self, line, for_create, for_task, is_modificated):
        """
        Prepara una línea de sección para las líneas de planificación.
        
        :param line: Línea de planificación.
        :param for_create: Indica si la línea es para creación.
        :param for_task: Indica si la línea es para tareas.
        :param is_modificated: Indica si la línea ha sido modificada.
        :return: Línea de sección preparada.
        """
        return (0, 0, {
            'name': line.name + ' * ' + str(line.product_uom_qty) if for_task and not is_modificated else line.name,
            'display_type': line.display_type or 'line_section',
            'description': False,
            'sequence': 0,
            'use_project_task': True,
            'planned_date_begin': False,
            'planned_date_end': False,
            'project_plan_pickings': False,
            'task_timesheet_id': False,
            'for_create': for_create,
            'for_modification': True,
            'service_qty': 0,
            'for_picking': True,
            'not_modificable': False
        })

    def prep_plan_lines(self, line):
        """
        Prepara las líneas de planificación basadas en las líneas de productos.
        
        :param line: Línea de producto.
        :return: Lista de líneas de planificación preparadas.
        """
        plan_lines = []
        for plan in line.product_id.project_plan_id.project_plan_lines:
            plan_lines.append((0, 0, {
                'name': plan.name + ' * ' + str(line.product_uom_qty),
                'description': plan.description,
                'use_project_task': True,
                'sequence': 0,
                'planned_date_begin': fields.Datetime.now(),
                'planned_date_end': fields.Datetime.now(),
                'project_plan_pickings': plan.project_plan_pickings.id,
                'task_timesheet_id': plan.task_timesheet_id.id,
                'display_type': False,
                'for_create': True,
                'for_modification': plan.for_modification,
                'service_qty': line.product_uom_qty,
                'for_picking': True,
                'not_modificable': plan.not_modificable
            }))
        return plan_lines

    def prep_picking_lines(self, line):
        """
        Prepara las líneas de picking basadas en las líneas de planificación.
        
        :param line: Línea de planificación.
        :return: Lista de líneas de picking preparadas.
        """
        picking_lines = []
        for picking in line.project_plan_pickings.project_picking_lines:
            picking_lines.append((0, 0, {
                'name': picking.product_id.name,
                'product_id': picking.product_id.id,
                'product_uom': picking.product_uom.id,
                'sequence': 0,
                'product_packaging_id': picking.product_packaging_id.id,
                'product_uom_qty': picking.product_uom_qty,
                'quantity': picking.quantity * line.service_qty,
                'standard_price': picking.standard_price,
                'subtotal': picking.subtotal,
                'display_type': False,
                'for_create': True,
                'for_modification': False,
                'last_price': picking.standard_price,
                'not_modificable': picking.not_modificable
            }))
        return picking_lines

    def action_open_create_project_wizard(self):
        """
        Abre el wizard para crear o modificar un proyecto.
        """
        self.ensure_one()
        project_name = []
        project_description = []

        if self.project_name:
            project_name = self.project_name
        else:
            project_name = self.project_id.name
            project_description = self.project_id.description

        context = {
            'default_sale_order_id': self.id,
            'default_actual_sale_order_id': self.id,
            'default_project_name': project_name,
            'default_description': project_description
        }

        if self.project_id:
            context['default_project_id'] = self.project_id.id

        if self.edit_project:
            return {
                'name': 'Project Version History',
                'view_mode': 'form',
                'res_model': 'project.version.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{
                    'default_project_id': self.project_id.id,
                    'default_modified_by': self.env.user.id,
                    'default_modification_date': fields.Datetime.now(),
                    'default_location_id': self.project_id.location_id.id,
                    'default_location_dest_id': self.project_id.location_dest_id.id,
                    'default_scheduled_date': self.project_id.scheduled_date,
                    'default_picking_type_id': self.project_id.default_picking_type_id.id,
                    'default_sale_order_id': self.id,
                    'default_plan_total_cost': self.plan_total_cost,
                    'default_date_start': self.project_id.date_start,
                    'default_date': self.project_id.date
                }
            }

        else:
            return {
                'name': project_name,  
                'view_mode': 'form',  
                'res_model': 'project.creation.wizard',  
                'type': 'ir.actions.act_window',  
                'target': 'new',  
                'context': {
                    'default_sale_order_id': self.id,
                    'default_client_id': self.partner_id.id,
                    'default_actual_sale_order_id': self.id,
                    'default_project_name': project_name,
                    'default_description': project_description
                }
            }

    def clean_duplicates_after_modification(self):
        """
        Limpia las líneas duplicadas después de modificar un proyecto.
        """
        for sale in self:
            lines_to_remove_picking = sale.project_picking_lines.filtered(
                lambda line: not line.for_create and not line.for_newlines and not line.for_modification and not line.display_type
            )
            if lines_to_remove_picking:
                lines_to_remove_picking.unlink()

    def project_lines_created(self):
        """
        Marca las líneas de planificación y picking como no nuevas después de su creación.
        """
        for sale in self.order_line:
            sale.not_modificable = True
        for sale in self.project_plan_lines:
            sale.for_newlines = False
            sale.not_modificable = True
        for sale in self.project_picking_lines:
            sale.for_newlines = False
            sale.not_modificable = True
        for sale in self.task_time_lines:
            sale.not_modificable = True
        
    def action_open_report(self):
        """
        Abre el reporte de análisis del proyecto.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'project_plan_templates.report_analytics', 
            'report_type': 'qweb-pdf',
            'res_model': 'sale.order',
            'res_id': self.id,
            'context': self.env.context,
        }
        
    def _get_report_values(self, docids, data=None):
        """
        Obtiene los valores necesarios para generar el reporte.
        
        :param docids: IDs de los documentos.
        :param data: Datos adicionales.
        :return: Diccionario con los valores para el reporte.
        """
        docs = self.env['sale.order'].browse(docids)  
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }