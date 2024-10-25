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

    @api.model_create_single
    def create(self, vals):
        """ Override create method to ensure that a project is created when the record is saved. """
        record = super(ProjectPlan, self).create(vals)
        if not record.project_name:
            raise ValidationError("Project name is required to create a project.")
        
        record.action_create_project()
        return record

    def action_create_project(self):
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

        self.create_project_tasks(project)
        self.project_name = False
        return project

    def create_project_tasks(self, project):
        current_task_type = None
        for line in self.project_plan_lines:
            if line.stage_id:
                current_task_type = self.get_or_create_task_type(line.stage_id, project)
            
            if not line.stage_id:
                current_task_type = self.get_or_create_task_type('Extras', project)

            self.env['project.task'].create({
                'name': line.name,
                'project_id': project.id,
                'stage_id': current_task_type.id,
            })

    def get_or_create_task_type(self, stage_id, project):
        task_type = self.env['project.task.type'].search([
            ('name', '=', stage_id),
            ('project_ids', 'in', project.id)
        ], limit=1)

        if not task_type:
            task_type = self.env['project.task.type'].create({
                'name': stage_id,
                'project_ids': [(4, project.id)],
            })
        
        return task_type