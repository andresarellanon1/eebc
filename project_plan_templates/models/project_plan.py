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
        string="Picking Lines",
        compute='_compute_picking_lines',
        store=False
    )

    @api.onchange('project_plan_pickings')
    def _compute_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines

    def action_create_project(self):
        if not self.project_name:
            raise ValidationError("Project name is required to create a project.")

        project_plan_lines_vals = [(0, 0, {
            'name': line.name,
            'chapter': line.chapter,
            'description': line.description,
            'use_project_task': line.use_project_task,
            'planned_date_begin': line.planned_date_begin,
            'planned_date_end': line.planned_date_end,
            'partner_id': [(6, 0 , line.partner_id.ids)],
            'stage_id': line.stage_id,
        }) for line in self.project_plan_lines]

        picking_lines_vals = [(0, 0, {
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }) for line in self.picking_lines]
        
        project_vals = {
            'name': self.project_name,
            'project_plan_id': self.id,
            'description': self.description,
            'project_picking_ids': [(6, 0, self.project_plan_pickings.ids)],
            'project_plan_lines': project_plan_lines_vals,
            'project_picking_lines': picking_lines_vals,

        }
        project = self.env['project.project'].create(project_vals)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'new',
        }