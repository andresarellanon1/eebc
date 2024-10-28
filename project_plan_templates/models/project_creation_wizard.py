from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Project Plan", required=True)
    project_name = fields.Char(related='project_plan_id.project_name', string="Project Name")
    user_id = fields.Many2one('res.users', string="Project manager")
    description = fields.Html(string="Description")
    project_plan_lines = fields.One2many(
        'project.plan.line', 
        'project_plan_id', 
        string="Project Plan Lines", 
        related='project_plan_id.project_plan_lines'
    )
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Picking Templates", 
        related='project_plan_id.project_plan_pickings'
    )
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        string="Picking Lines",
        compute='_compute_picking_lines'
    )

    @api.depends('project_plan_id')
    def _compute_picking_lines(self):
        for wizard in self:
            wizard.picking_lines = wizard.project_plan_id.picking_lines

    def action_confirm_create_project(self):
        self.ensure_one()
        
        return self.project_plan_id.action_create_project()