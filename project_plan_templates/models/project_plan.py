from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Nombre", required=True)
    project_name = fields.Char(string="Project name")
    description = fields.Html(string="Descripción")
    note = fields.Char()

    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Proyecto")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Movimientos de inventario")
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        compute="_compute_picking_lines",
        string="Picking Lines",
        store=True
    )

    task_time_lines = fields.One2many('task.time.lines',
        'project_plan_id',
        string="Mano de obra",
        compute="_compute_task_lines",
        store = True
        )

    plan_total_cost = fields.Float(string="Costo total", compute="_compute_total_cost", default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string="Servicio",
        ondelete='restrict',
    )

    service_project_domain = fields.Many2many('product.template', store=True, compute="_compute_service_project_domain")

    # @api.constrains('project_plan_lines', 'picking_lines')
    # def _check_lines_existence(self):
    #     for record in self:
    #         if not record.project_plan_lines:
    #             raise ValidationError("Debe agregar al menos una línea en la pestaña 'Tasks'.")
    #         if not record.picking_lines:
    #             raise ValidationError("Debe agregar al menos una línea en la pestaña 'Stock'.")

    # @api.constrains('product_template_id')
    # def _check_unique_product_template(self):
    #     for record in self:
    #         if record.product_template_id:
    #             duplicates = self.search([('product_template_id', '=', record.product_template_id.id), ('id', '!=', record.id)])
    #             if duplicates:
    #                 raise ValidationError("El producto '%s' ya está asignado a otro proyecto." % record.product_template_id.display_name)


    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.picking_lines)

    @api.depends('project_plan_lines')
    def _compute_picking_lines(self):
        for record in self:
            record.picking_lines = [(5, 0, 0)]
            record.picking_lines = record.get_picking_lines(record.project_plan_lines)

    @api.depends('project_plan_lines')
    def _compute_task_lines(self):
        for record in self:
            record.task_time_lines = [(5, 0, 0)]
            record.task_time_lines = record.get_task_time_lines(record.project_plan_lines)

    def get_picking_lines(self, line):
        picking_lines = []

        for picking in line:
            picking_lines += self.prep_picking_lines(picking)
                
        return picking_lines

    def get_task_time_lines(self, line):
        task_lines = []

        for task in line:
            task_lines += self.prep_task_time_lines(task)

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
    
    def prep_task_time_lines(self, line):
        task_lines = []
        for task in line.task_timesheet_id.task_time_lines:
            task_lines.append((0, 0, {
                'description': task.description,
                'estimated_time': task.estimated_time,
                'work_shift': task.work_shift
            }))
        
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

    @api.model
    def write(self, vals):
        result = super(ProjectPlan, self).write(vals)
        if 'product_template_id' in vals and vals['product_template_id']:
            product_template = self.env['product.template'].browse(vals['product_template_id'])
            if product_template and product_template.project_plan_id != self:
                product_template.write({'project_plan_id': self.id})

        return result
