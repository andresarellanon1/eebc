from odoo import fields, api, models
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    project_plan_id = fields.Many2one('project.plan', string="Project template")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines")

    @api.onchange('project_plan_id')
    def plan_lines(self):
        for project in self:
            project.project_picking_lines = [(5, 0, 0)]

            if project.project_plan_id:
                project.project_plan_lines = [(6, 0, project.project_plan_id.project_plan_lines.ids)]
                project.description = project.project_plan_id.description
                project.project_picking_ids = [(6, 0, project.project_plan_id.project_plan_pickings.ids)]
            else:
                project.project_plan_lines = [(5, 0, 0)]
                project.description = False
                project_plan_pickings = [(5, 0, 0)]

    @api.onchange('project_picking_ids')
    def update_picking_lines(self):
        for project in self:
            project.project_picking_lines = [(5, 0, 0)]

            lines = self.env['project.picking.lines']
            for picking in project.project_picking_ids:
                lines |= picking.project_picking_lines
            
            project.project_picking_lines = [(6, 0, lines.ids)]