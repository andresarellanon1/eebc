from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Project Plan", required=True)
    project_name = fields.Char(string="Project Name")
    user_id = fields.Many2one('res.users', string="Project manager")
    description = fields.Html(string="Description")
    project_plan_lines = fields.One2many(
        'project.plan.line', 
        'project_plan_wizard_id', 
        string="Project Plan Lines"
    )
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Picking Templates"
    )
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_wizard_id',
        string="Picking Lines",
        compute='_compute_picking_lines',
        store=False
    )

    @api.onchange('project_plan_id')
    def _onchange_project_plan_id(self):
        if self.project_plan_id:
            self.project_name = self.project_plan_id.project_name
            self.project_plan_lines = self.project_plan_id.project_plan_lines
            self.project_plan_pickings = self.project_plan_id.project_plan_pickings
            self.picking_lines = self.project_plan_id.picking_lines

    @api.onchange('project_plan_pickings')
    def _compute_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines

    def action_confirm_create_project(self):
        self.ensure_one()
        
        return self.project_plan_id.action_create_project()