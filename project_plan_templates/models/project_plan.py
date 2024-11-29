from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Name", required=True)
    project_name = fields.Char(string="Project name")
    description = fields.Html(string="Description")
    note = fields.Char()

    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Project")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        string="Picking Lines"
    )

    plan_total_cost = fields.Float(string="Total cost", compute='_compute_total_cost', default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string="Servicio",
        ondelete='restrict',  
        inverse_name='project_plan_id'
    )

    service_project_domain = fields.Many2many('product.template', store=True, compute="_compute_service_project_domain")

    @api.constrains('product_template_id')
    def _check_unique_product_template(self):
        for record in self:
            if record.product_template_id:
                duplicates = self.search([('product_template_id', '=', record.product_template_id.id), ('id', '!=', record.id)])
                if duplicates:
                    raise ValidationError("El producto '%s' ya está asignado a otro proyecto." % record.product_template_id.display_name)


    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.picking_lines)


    @api.onchange('project_plan_pickings')
    def onchange_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines


    def action_open_create_project_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create Project',
            'view_mode': 'form',
            'res_model': 'project.creation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_plan_id': self.id,
                'default_project_plan_pickings': [(6, 0, self.project_plan_pickings.ids)],
                'default_picking_lines': [(6, 0, self.picking_lines.ids)],
                'default_description': self.description,
            }
        }


    @api.depends('product_template_id')
    def _compute_service_project_domain(self):
        for record in self:
            service = self.env['product.template'].search([
                ('detailed_type', '=', 'service'),
                ('service_tracking', '=', 'project_only'),
                ('project_plan_id', '=', False),
                ('sale_ok', '=', True),
            ])
            record.service_project_domain = [(6, 0, service.ids)]

    @api.model
    def write(self, vals):
        result = super(ProjectPlan, self).write(vals)
        if 'product_template_id' in vals and vals['product_template_id']:
            product_template = self.env['product.template'].browse(vals['product_template_id'])
            if product_template and product_template.project_plan_id != self:
                product_template.write({'project_plan_id': self.id})

        return result