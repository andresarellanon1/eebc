from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Project Plan", required=True, readonly="True")
    project_name = fields.Char(string="Project Name")
    user_id = fields.Many2one('res.users', string="Project manager")
    description = fields.Html(string="Description")
    project_plan_lines = fields.Many2many(
        'project.plan.line', 
        string="Project Plan Lines"
    )
    
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Picking Templates"
    )

    picking_lines = fields.Many2many(
        'project.picking.lines',
        string="Picking Lines"
    )

    @api.onchange('project_plan_id')
    def _onchange_project_plan_id(self):
        if self.project_plan_id:
            self.project_name = self.project_plan_id.project_name
            self.project_plan_lines = self.project_plan_id.project_plan_lines
            self.project_plan_pickings = self.project_plan_id.project_plan_pickings
            self.picking_lines = self.project_plan_id.picking_lines
            self.description = self.project_plan_id.description

    @api.onchange('project_plan_pickings')
    def onchange_picking_lines(self):
        for record in self:
            lines = self.env['project.picking.lines']
            for picking in record.project_plan_pickings:
                lines |= picking.project_picking_lines
            record.picking_lines = lines.filtered('product_id')

    def action_confirm_create_project(self):
        self.ensure_one()

        project_plan_lines_vals = [(0, 0, {
            'name': line.name,
            'chapter': line.chapter,
            'description': line.description,
            'use_project_task': line.use_project_task,
            'planned_date_begin': line.planned_date_begin,
            'planned_date_end': line.planned_date_end,
            'task_timesheet_id': line.task_timesheet_id.id,
            'partner_id': [(6, 0, line.partner_id.ids)],
            'stage_id': line.stage_id,
        }) for line in self.project_plan_lines if line.use_project_task]

        picking_lines_vals = [(0, 0, {
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }) for line in self.picking_lines]

        project_vals = {
            'name': self.project_name,
            'description': self.description,
            'project_plan_lines': project_plan_lines_vals,
            'project_picking_lines': picking_lines_vals,
        }

        project = self.env['project.project'].create(project_vals)
        self.create_project_tasks(project)

        self.project_plan_id.project_name = False

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def create_project_tasks(self, project):
        current_task_type = None
        for line in self.project_plan_lines:
            if line.stage_id:
                current_task_type = self.get_or_create_task_type(line.stage_id, project)
            else:
                current_task_type = self.get_or_create_task_type('Extras', project)

            if line.use_project_task:
                timesheet_lines = self.env['task.time.lines'].search([
                    ('task_timesheet_id', '=', line.task_timesheet_id.id)
                ])

                timesheet_data = [(0, 0, {
                    'name': ts_line.description,
                    'estimated_time': ts_line.estimated_time,
                }) for ts_line in timesheet_lines]

                self.env['project.task'].create({
                    'name': line.name,
                    'project_id': project.id,
                    'stage_id': current_task_type.id,
                    'user_ids': line.partner_id.ids,
                    'timesheet_ids': timesheet_data,
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