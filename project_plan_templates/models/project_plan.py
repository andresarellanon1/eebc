from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Name", required=True)
    project_name = fields.Char(string="Project name")
    description = fields.Html(string="Description")
    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Project")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Picking Templates")

    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        string="Picking Lines"
    )

    plan_total_cost = fields.Float(string="Total cost", default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    note = fields.Char()

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
                'default_project_plan_lines': [(6, 0, self.project_plan_lines.ids)],
                'default_project_plan_pickings': [(6, 0, self.project_plan_pickings.ids)],
                'deafult_picking_lines': [(6, 0, self.picking_lines.ids)],
                'default_description': self.description,
            }
        }

    @api.onchange('project_plan_pickings')
    def calculate_project_plan_cost(self):
        total_cost = 0.0

        for record in self.project_plan_pickings:
            total_cost += record.subtotal
        
        self.plan_total_cost = total_cost