from odoo import fields, api, models
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'
    
    project_plan_id = fields.Many2one('project.plan', string="Project template")
    project_plan_description = fields.Char(string="Project description")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2one('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project picking lines")

    @api.onchange('project_plan_id', 'project_picking_ids')
    def plan_lines(self):
        for project in self:
            project.project_picking_lines = [(5, 0, 0)]  
            
            if project.project_plan_id:
                project.project_plan_lines = [(6, 0, project.project_plan_id.project_plan_lines.ids)]
                project.project_plan_description = project.project_plan_id.description

            for picking in project.project_picking_ids:
                separator = self.env['project.plan.picking.line'].create({
                    'project_plan_id': project.id,
                    'product_id': False,
                    'quantity': 0,
                    'location_id': False,
                    'picking_name': picking.name
                })
                project.project_picking_lines += separator

                for line in picking.product_ids:
                    project.project_picking_lines += line

            if not project.project_plan_id:
                project.project_plan_lines = [(5, 0, 0)]
                project.project_plan_description = False