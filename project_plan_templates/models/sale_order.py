from odoo import fields, models, api
import json
import logging
logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Is project?", default=False)
    project_name = fields.Char(string="Project title")

    state = fields.Selection(
        selection_add=[
            ('estimation', 'Estimation'),
            ('budget', 'Budget')
        ],
        ondelete={
            'estimation': 'set default',
            'budget': 'set default'
        }
    )

    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')
    project_picking_lines = fields.One2many('project.picking.lines', 'sale_order_id')
    total_product_cost = fields.Float(string="Total cost",  compute='_compute_total_cost', default=0.0)

    @api.onchange('is_project')
    def _onchange_is_project(self):
        for record in self:
            record.order_line = None


    def _compute_total_product_cost(self):
        for order in self:
            total_cost = 0.0
            for line in order.order_line:
                # Calcular el costo de cada línea de producto
                if line.product_id:
                    total_cost += line.product_id.standard_price * line.product_uom_qty
            order.total_product_cost = total_cost

    def action_confirm(self):
        self.ensure_one()
        for sale in self:
            if sale.is_project:
                sale.project_plan_lines = [(5, 0, 0)]
                sale.project_picking_lines = [(5, 0, 0)]

                sale.state = 'estimation'
                plan_lines = []
                picking_lines = []
                for line in sale.order_line:
                    if line.display_type == 'line_section':
                        plan_lines.append((0, 0, {
                            'name': line.name,
                            'display_type': line.display_type,
                            'description': False,
                            'task_timesheet_id': False,
                        }))
                        picking_lines.append((0, 0, {
                            'name': line.name,
                            'display_type': line.display_type,
                            'product_id': False,
                            'quantity': False,
                            'standard_price': False,
                            'subtotal': False
                        }))
                    else:
                        for plan in line.product_id.project_plan_id.project_plan_lines:
                            plan_lines.append((0, 0, {
                                'name': f"{line.product_id.default_code}-{line.product_template_id.name}-{plan.name}",
                                'description': plan.description,
                                'task_timesheet_id': plan.task_timesheet_id.id,
                                'display_type': False
                            }))
                        for picking in line.product_id.project_plan_id.picking_lines:
                            picking_lines.append((0, 0, {
                                'name': picking.product_id.name,
                                'product_id': picking.product_id.id,
                                'quantity': picking.quantity,
                                'standard_price': picking.standard_price,
                                'subtotal': picking.subtotal,
                                'display_type': False
                            }))
                sale.project_plan_lines = plan_lines
                sale.project_picking_lines = picking_lines
            else:
                return super(SaleOrder, self).action_confirm()

    def action_create_project(self):
        self.ensure_one()
        for sale in self:
            sale.state == 'budget'

    
            