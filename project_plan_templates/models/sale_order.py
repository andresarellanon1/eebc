from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import json
import logging

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Es proyecto?", default=False)
    project_name = fields.Char(string="Titulo de proyecto")
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    state = fields.Selection(
        selection_add=[
            ('budget', 'Presupuesto'),
            ('process', 'En proceso'),
        ],
        ondelete={'budget': 'set default', 'process': 'set default'},
    )

    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")
    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')
    # project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id', compute="_compute_picking_lines", store=True)

    project_id = fields.Many2one('project.project', string="Proyecto")

    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id')
    edit_project = fields.Boolean(string="Modificar proyecto", default=False)

    is_editable = fields.Boolean(
        string='Editable',
        compute='_compute_is_editable',
        store=True
    )

    # task_time_lines = fields.One2many(
    #     'task.time.lines',
    #     'sale_order_id',
    #     string="Lineas de mano obra",
    #     compute="_compute_task_lines",
    #     store=True)
    task_time_lines = fields.One2many(
        'task.time.lines',
        'sale_order_id',
        string="Lineas de mano obra")

    labour_total_cost = fields.Float(string="Costo mano de obra", compute="_compute_labour_cost", default=0.0)

    # @api.depends('project_plan_lines')
    #def _compute_task_time_lines(self):
    def update_task_lines(self):
        for record in self:
            record.task_time_lines = [(5, 0, 0)]
            record.task_time_lines = record.get_task_time_lines(record.project_plan_lines)

    def get_task_time_lines(self, line):
        task_lines = []
        for task in line:
            if task.display_type == 'line_section':
                task_lines.append(self.prep_task_line_section_line(task))
            else:
                for _ in range(int(task.service_qty)):
                    task_lines += self.prep_task_time_lines(task)
            #task_lines += self.prep_task_time_lines(task)

        return task_lines

    def prep_task_time_lines(self, line):
        task_lines = []
        for task in line.task_timesheet_id.task_time_lines:
            task_lines.append((0, 0, {
                'product_id': task.product_id.id,
                'description': task.description,
                'estimated_time': task.estimated_time,
                'work_shift': task.work_shift,
                'unit_price': task.unit_price,
                'price_subtotal': task.price_subtotal
            }))
        return task_lines

    @api.depends('task_time_lines.price_subtotal')
    def _compute_labour_cost(self):
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
        for record in self:
            #record.project_picking_lines = [(5, 0, 0)]  # Limpiar líneas existentes
            record.project_picking_lines = record.get_picking_lines(record.project_plan_lines)

    def get_picking_lines(self, line):
        picking_lines = []

        for picking in line:
            if picking.for_picking:
                if picking.for_create:
                    if picking.display_type == 'line_section':
                        picking_lines.append(self.prep_picking_section_line(picking, True, False))
                    else:
                        if picking.for_create:
                            picking_lines += self.prep_picking_lines(picking)
                else:
                    picking_lines.append(self.prep_picking_section_line(picking, False, True))

                picking.for_picking = False
                picking.for_modification = False
                
        return picking_lines
    
    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.onchange('is_project')
    def _onchange_is_project(self):
        for record in self:
            record.order_line = None
            if not record.is_project and record.edit_project:
                record.edit_project = False
                record.project_id = False

    def action_generate_planning(self):
        self.ensure_one()
        
        for sale in self:
            if sale.is_project:
                if not sale.project_name and not sale.edit_project:
                    raise ValidationError(
                        f"se requiere el nombre del proyecto"
                    ) 

                plan_pickings = []
                plan_lines = []
                for line in sale.order_line:
                    if line.for_modification:
                        if line.display_type == 'line_section':
                            plan_lines.append(self.prep_plan_section_line(line, True, False))
                        else:
                            if line.product_id.project_plan_id:
                                plan_lines.append(self.prep_plan_section_line(line, False, True))
                                plan_lines += self.prep_plan_lines(line)

                            for project_picking in line.product_id.project_plan_id.project_plan_pickings:
                                plan_pickings.append((4, project_picking.id))
                        line.for_modification = False

                for plan in sale.project_plan_lines:
                    if plan.for_modification:
                        plan.for_modification = False

                sale.project_plan_pickings = plan_pickings
                sale.project_plan_lines = plan_lines

                sale.update_picking_lines()
                sale.update_task_lines()

            sale.state = 'budget'
            

    @api.onchange('project_id')
    def _compute_order_lines_from_project_previous_version(self):
        for sale in self:
            sale.order_line = [(5, 0, 0)]
            sale.project_plan_lines = [(5, 0, 0)]
            sale.project_picking_lines = [(5, 0, 0)]
            if sale.edit_project and sale.project_id and sale.project_id.actual_sale_order_id:

                previous_order = sale.project_id.actual_sale_order_id

                sale.partner_id = previous_order.partner_id
                sale.project_name = previous_order.project_name

                sale.order_line = [(0, 0, {
                    'product_id': line.product_id.id,
                    'display_type': line.display_type,
                    'name': line.name + ' * ' + str(line.product_uom_qty),
                    'product_uom_qty': 0,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'for_modification': False
                }) for line in previous_order.order_line]

                # Copiar project_plan_lines directamente
                # Preparar y asignar líneas de plan
                plan_lines = self._prepare_plan_lines(previous_order.project_plan_lines)
                sale.project_plan_lines = plan_lines

                # Preparar y asignar líneas de picking
                picking_lines = self._prepare_picking_lines(previous_order.project_picking_lines)
                sale.project_picking_lines = picking_lines

    def _prepare_plan_lines(self, lines):
        """Prepara las líneas de plan para asignarlas al pedido."""
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
            'for_picking': line.for_picking
        }) for line in lines]

    def _prepare_picking_lines(self, lines):
        """Prepara las líneas de picking para asignarlas al pedido."""
        return [(0, 0, {
            'name': line.name,
            'sequence': line.sequence,
            'display_type': line.display_type,
            'product_id': line.product_id.id if line.product_id else False,
            'product_uom': line.product_uom.id if line.product_uom else False,
            'product_packaging_id': line.product_packaging_id.id if line.product_packaging_id else False,
            'product_uom_qty': line.product_uom_qty,
            'quantity': line.quantity,
            'standard_price': line.standard_price,
            'subtotal': line.subtotal,
            'for_create': line.for_create,
            'for_modification': False
        }) for line in lines]

    def prep_task_line_section_line(self, line):
        return(0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'product_id':  False,
            'description':  False,
            'estimated_time':  False,
            'work_shift':  False,
            'unit_price':  False,
            'price_subtotal': False
        })
    
    def prep_picking_section_line(self, line, for_create, for_task):
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
            'for_modification': False
        })
    
    def prep_plan_section_line(self, line, for_create, for_task):
        return (0, 0, {
            'name': line.name + ' * ' + str(line.product_uom_qty) if for_task else line.name,
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
        })

    def prep_plan_lines(self, line):
        plan_lines = []
        for plan in line.product_id.project_plan_id.project_plan_lines:
            plan_lines.append((0, 0, {
                #'name': f"{line.product_template_id.name}-{plan.name}",
                'name': plan.name + ' * ' + line.product_uom_qty,
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
                'for_picking': True
            }))
        return plan_lines

    def prep_picking_lines(self, line):
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
                'for_modification': False
            }))
        return picking_lines

    def action_open_create_project_wizard(self):
        
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
        Solo limpia las líneas con for_modification=True.
        """
        for sale in self:
            lines_to_remove = sale.project_plan_lines.filtered('for_modification')
            lines_to_remove.unlink()

            lines_to_remove_picking = sale.project_picking_lines.filtered('for_modification')
            lines_to_remove_picking.unlink()

    def project_lines_created(self):
        for sale in self.project_plan_lines:
            sale.for_newlines == False
        for sale in self.project_picking_lines:
            sale.for_newlines == False
        
    def action_open_report(self):
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
        docs = self.env['sale.order'].browse(docids)  
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }