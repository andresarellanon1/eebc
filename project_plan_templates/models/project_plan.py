from odoo import fields, models, api
from odoo.exceptions import ValidationError

# Model for managing project plan templates. This model serves
# as a template for creating projects, containing project configurations,
# task lines, and inventory picking templates with their associated costs.
class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    # Basic template information
    name = fields.Char(string="Name", required=True)
    project_name = fields.Char(string="Project name")
    description = fields.Html(string="Description")
    note = fields.Char()

    # Relation fields for project and line management
    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Project")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        string="Picking Lines"
    )

    # Computed and company fields
    plan_total_cost = fields.Float(string="Total cost", compute='_compute_total_cost', default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string="Servicio",
        ondelete='restrict',  # Evita borrar accidentalmente el producto
        inverse_name='project_plan_id'
    )

    # Define the Many2many field for service product domains
    service_project_domain = fields.Many2many('product.template', store=True, compute="_compute_service_project_domain")

    # Validates that a product template is assigned only once to a project plan.
    @api.constrains('product_template_id')
    def _check_unique_product_template(self):
        for record in self:
            if record.product_template_id:
                duplicates = self.search([('product_template_id', '=', record.product_template_id.id), ('id', '!=', record.id)])
                if duplicates:
                    raise ValidationError("El producto '%s' ya está asignado a otro proyecto." % record.product_template_id.display_name)

    # Computes the total cost of the project plan by summing
    # the subtotals of all picking lines. Updates
    # whenever the subtotals of picking lines change.
    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.picking_lines)

    # This method allows the user to select multiple inventory templates
    # and combines all their products into a single list.
    # When the 'project_plan_pickings' field is modified,
    # it aggregates the 'project_picking_lines' from each selected picking
    # and assigns the combined list to 'picking_lines' in the current record.
    @api.onchange('project_plan_pickings')
    def onchange_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines

    # This action opens a wizard to create a project from the current template.
    # It allows the user to generate the project's tasks, timesheets, and inventory.
    # The wizard is displayed in a form view and opens as a modal dialog.
    # The context now includes the following default values for the wizard:
    # - 'default_project_plan_id': the current template's ID
    # - 'default_project_plan_lines': the IDs of the project plan lines
    # - 'default_project_plan_pickings': the IDs of the inventory templates
    # - 'default_picking_lines': the IDs of the picking lines
    # - 'default_description': the current template's description
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

    # Computes the domain of service products that are available for the project
    # by checking if they are of type service, have project tracking, and are not yet
    # assigned to a project plan.
    @api.depends('product_template_id')
    def _compute_service_project_domain(self):
        # Evitar recursión infinita: Sólo actualiza cuando sea necesario
        for record in self:
            service = self.env['product.template'].search([
                ('detailed_type', '=', 'service'),
                ('service_tracking', '=', 'project_only'),
                ('project_plan_id', '=', False),
                ('sale_ok', '=', True),
            ])
            record.service_project_domain = [(6, 0, service.ids)]

    # Prevents recursion when saving both project plan and product template changes.
    @api.model
    def write(self, vals):
        
        result = super(ProjectPlan, self).write(vals)
        # Evitar recursión infinita: Actualizar solo cuando sea necesario
        if 'product_template_id' in vals and vals['product_template_id']:
            product_template = self.env['product.template'].browse(vals['product_template_id'])
            if product_template and product_template.project_plan_id != self:
                product_template.write({'project_plan_id': self.id})
        else:
            service = self.env['product.template'].search([
                ('project_plan_id', '=', self.id),
            ])
            service.write({'project_plan_id': False})
        return result