from odoo import fields, models, api
from odoo.exceptions import ValidationError

# Model for managing project plan templates. This model serves
# as a template for creating projects, containing project configurations,
# task lines, and inventory picking templates with their associated costs.
class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    # Basic template information fields
    name = fields.Char(string="Name", required=True)
    product_template_ids = fields.Many2one('product.template',string="Servicio")
    service_project_domain = fields.Many2many('product.template', store=True, compute="_compute_service_project_domain")
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
    plan_total_cost = fields.Float(string="Total cost",  compute='_compute_total_cost', default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

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

    # Computes the total cost of the project plan by summing
    # the subtotals of all picking lines. Updates 
    # whenever the subtotals of picking lines change.
    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.picking_lines)

    @api.onchange('service_project_domain','product_template_ids.project_plan_id')
    def _compute_service_project_domain(self):
        for record in self:
            service = self.env['product.template'].search([
                ('detailed_type', '=', 'service'),
                ('service_tracking', '=', 'project_only'),
                ('project_plan_id', '=', False),
                ('sale_ok', '=', True),
            ])
            record.service_project_domain = [(6, 0, service.ids)]

    # def write(self, vals):
    #     self._compute_service_project_domain
    #     self.product_template_ids.project_plan_id = self.id
    #     result = super(ProjectPlan, self).write(vals)
    #     return result

