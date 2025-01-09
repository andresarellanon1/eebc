from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import json
import logging
logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Es proyecto?", default=False)
    project_name = fields.Char(string="Titulo de proyecto")
    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)

    state = fields.Selection(
        selection_add=[
            ('budget', 'Budget'),
            ('process', 'In process')
        ],
        ondelete={
            'budget': 'set default',
            'process': 'set default'
        }
    )

    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")
    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')
    # project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id', compute="_compute_picking_lines", store=True)

    project_id = fields.Many2one('project.project', string="Proyecto")

    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id')
    edit_project = fields.Boolean(string="Modificar proyecto", default=False)

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        record.update_picking_lines()
        return record

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'project_plan_lines' in vals:
            self.update_picking_lines()
        return res

    def update_picking_lines(self):
        for record in self:
            record.project_picking_lines = [(5, 0, 0)]  # Limpiar líneas existentes
            record.project_picking_lines = record.get_picking_lines(record.project_plan_lines)

    def get_picking_lines(self, line):
        picking_lines = []

        for picking in line:
            if picking.display_type == 'line_section':
                picking_lines.append(self.prep_picking_section_line(picking))
            else:
                picking_lines.append(self.prep_picking_section_line(picking))
                picking_lines += self.prep_picking_lines(picking)
                
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
                if not sale.project_name:
                    raise ValidationError(
                        f"se requiere el nombre del proyecto"
                    )
                sale.project_plan_pickings = [(5, 0, 0)]
                sale.project_plan_lines = [(5, 0, 0)]

                plan_pickings = []
                plan_lines = []
                for line in sale.order_line:
                    if line.display_type == 'line_section':
                        plan_lines.append(self.prep_plan_section_line(line, True))
                    else:
                        if line.product_id.project_plan_id:
                            plan_lines.append(self.prep_plan_section_line(line, False))
                            plan_lines += self.prep_plan_lines(line)

                        for project_picking in line.product_id.project_plan_id.project_plan_pickings:
                            plan_pickings.append((4, project_picking.id))

                sale.project_plan_pickings = plan_pickings
                sale.project_plan_lines = plan_lines
            

    @api.onchange('project_id')
    def _compute_order_lines_from_project_previous_version(self):
        for sale in self:
            if sale.edit_project and sale.project_id and sale.project_id.sale_order_id:
                previous_order = sale.project_id.sale_order_id

                new_order_lines = []
                for line in previous_order.order_line:
                    new_line = {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                    }
                    new_order_lines.append((0, 0, new_line))
                sale.order_line = new_order_lines

                new_project_plan_lines = []
                for line in previous_order.project_plan_lines:
                    if line.display_type == 'line_section':
                        new_project_plan_lines.append(self.prep_plan_section_line(line, for_create=True))
                    else:
                        new_project_plan_lines.append(self.prep_plan_section_line(line, for_create=False))
                        new_project_plan_lines += self.prep_plan_lines(line)
                sale.project_plan_lines = new_project_plan_lines

                new_project_plan_pickings = []
                for line in previous_order.project_plan_pickings:
                    if line.display_type == 'line_section':
                        new_project_plan_pickings.append(self.prep_picking_section_line(line))
                    else:
                        new_project_plan_pickings += self.prep_picking_lines(line)
                sale.project_plan_pickings = new_project_plan_pickings
    
    def prep_picking_section_line(self, line):
        return (0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'product_id': False,
            'product_uom': False,
            'product_packaging_id': False,
            'product_uom_qty': False,
            'quantity': False,
            'standard_price': False,
            'subtotal': False
        })
    
    def prep_plan_section_line(self, line, for_create):
        return (0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'description': False,
            'use_project_task': True,
            'planned_date_begin': False,
            'planned_date_end': False,
            'project_plan_pickings': False,
            'task_timesheet_id': False,
            'for_create': for_create
        })

    def prep_plan_lines(self, line):
        plan_lines = []
        for plan in line.product_id.project_plan_id.project_plan_lines:
            plan_lines.append((0, 0, {
                #'name': f"{line.product_template_id.name}-{plan.name}",
                'name': plan.name,
                'description': plan.description,
                'use_project_task': True,
                'planned_date_begin': fields.Datetime.now(),
                'planned_date_end': fields.Datetime.now(),
                'project_plan_pickings': plan.project_plan_pickings.id,
                'task_timesheet_id': plan.task_timesheet_id.id,
                'display_type': False,
                'for_create': True
            }))
        return plan_lines

    def prep_picking_lines(self, line):
        picking_lines = []
        for picking in line.project_plan_pickings.project_picking_lines:
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
        return picking_lines

    def action_open_create_project_wizard(self):
        self.ensure_one()

        context = {
            'default_sale_order_id': self.id,
            'default_project_name': self.project_name,
        }

        if self.project_id:
            context['default_project_id'] = self.project_id.id

        return {
            'name': 'Projects creation',  
            'view_mode': 'form',  
            'res_model': 'project.creation.wizard',  
            'type': 'ir.actions.act_window',  
            'target': 'new',  
            'context': context,
        }
        
        
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
    
