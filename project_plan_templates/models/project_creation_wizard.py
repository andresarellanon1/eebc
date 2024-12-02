from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'

    project_plan_id = fields.Many2one('project.plan', string="Project Plan", readonly=True)
    project_name = fields.Char(string="Project Name", required=True)
    user_id = fields.Many2one('res.users', string="Project manager")
    description = fields.Html(string="Description")
    sale_order_id = fields.Many2one('sale.order', string="Sale order")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Picking Templates"
    )

    wizard_plan_lines = fields.One2many(
        'project.plan.wizard.line', 'wizard_id',
        string="Project Plan Lines"
    )

    wizard_picking_lines = fields.One2many(
        'project.picking.wizard.line', 'wizard_creation_id',
        string="Project Picking Lines"
    )

    note = fields.Char()

    plan_total_cost = fields.Float(string="Total cost",  compute='_compute_total_cost', default=0.0)

    @api.onchange('sale_order_id')
    def _compute_wizard_lines(self):
        for record in self:
            
            record.wizard_picking_lines = [(5, 0, 0)]
            record.wizard_plan_lines = [(5, 0, 0)]

            plan_lines = self.sale_order_id.prep_plan_lines(record.sale_order_id.project_plan_lines)
            picking_lines = self.sale_order_id.prep_picking_lines(record.sale_order_id.project_picking_lines)

            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines

    
    def action_confirm_create_project(self):
        self.ensure_one()

        project_plan_lines = self.sale_order_id.prep_plan_lines(self.sale_order_id.project_plan_lines)
        picking_line_vals = self.sale_order_id.prep_picking_lines(self.sale_order_id.project_picking_lines)

        project_vals = {
            'name': self.project_name,
            'description': self.description,
            'project_plan_lines': project_plan_lines,
            'project_picking_lines': picking_line_vals,
        }

        project = self.env['project.project'].create(project_vals)
        self.create_project_tasks(project)

        self.sale_order_id.state = 'budget'
        self.sale_order_id.project_id = project.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def create_project_tasks(self, project):
        current_task_type = None
        for line in self.wizard_plan_lines:
            if line.display_type:
                current_task_type = self.get_or_create_task_type(line.name, project)

            if line.use_project_task and not line.display_type:
                if not current_task_type:
                    current_task_type = self.get_or_create_task_type('Extras', project)

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

    @api.depends('wizard_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.wizard_picking_lines)