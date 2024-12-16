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
    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id', compute="_compute_picking_lines", store=True)

    project_id = fields.Many2one('project.project', string="Proyecto")
    
    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.onchange('is_project')
    def _onchange_is_project(self):
        for record in self:
            record.order_line = None

    def action_confirm(self):
        self.ensure_one()
        
        for sale in self:
            if sale.is_project:
                if not sale.project_name:
                    raise ValidationError(
                        f"Project name needed."
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
            return super(SaleOrder, self).action_confirm()
    
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
    
    def prep_plan_section_line(self, line, for_create:
        return (0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'description': False,
            'use_project_task': True,
            'planned_date_begin': False,
            'planned_date_end': False,
            'partner_id': False,
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
                'partner_id': [(6, 0, plan.partner_id.ids)],
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

    @api.depends('project_plan_lines')
    def _compute_picking_lines(self):
        for record in self:
            record.project_picking_lines = [(5, 0, 0)]
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

    def action_open_create_project_wizard(self):
        self.ensure_one()

        return {
            'name': 'Projects creation',  
            'view_mode': 'form',  
            'res_model': 'project.creation.wizard',  
            'type': 'ir.actions.act_window',  
            'target': 'new',  
            'context': {
                'default_sale_order_id': self.id,
                'default_project_name': self.project_name
            }
        }