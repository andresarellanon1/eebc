from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Html(string="Descripción")
    note = fields.Char()

    project_id = fields.Many2one('project.project', string="Proyecto")
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        compute="_compute_picking_lines",
        string="Picking Lines",
        store=True
    )

    plan_total_cost = fields.Float(string="Costo total", compute='_compute_total_cost', default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string="Servicio",
        ondelete='restrict',  
        inverse_name='project_plan_id'
    )

    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.picking_lines)

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