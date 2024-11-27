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

    @api.onchange('is_project')
    def _onchange_is_project(self):
        for record in self:
            record.order_line = None

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
                    for plan in line.product_id.project_plan_id.project_plan_lines:
                        logger.warning(f"Section: {line.display_type}")
                        if line.display_type == 'line_section':
                            logger.warning(f"Section: {line.name}")
                            plan_lines.append((0, 0, {
                                'name': line.name,
                                'display_type': line.display_type,
                                'description': False,
                                'task_timesheet_id': False,
                            }))
                        else:
                            logger.warning(f"Plan Lines: {line.name}")
                            plan_lines.append((0, 0, {
                                'name': f"{line.product_id.default_code}-{line.product_template_id.name}-{plan.name}",
                                'description': plan.description,
                                'task_timesheet_id': plan.task_timesheet_id.id,
                                'display_type': False
                            }))
                    for picking in line.product_id.project_plan_id.picking_lines:
                        if line.display_type == 'line_section':
                            picking_lines.append((0, 0, {
                                'name': line.name,
                                'display_type': line.display_type,
                                'product_id': False,
                                'quantity': False,
                                'standard_price': False,
                                'subtotal': False
                            }))
                        else:
                            picking_lines.append((0, 0, {
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

    
            