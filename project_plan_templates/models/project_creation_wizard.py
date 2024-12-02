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
    is_sale_order = fields.Boolean(default=False)
    sale_order_id = fields.Many2one('sale.order', string="Sale order")
    
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

            plan_lines = []
            picking_lines = []
            for line in record.sale_order_id.project_plan_lines:
                if line.use_project_task:
                    if line.display_type == 'line_section':
                        plan_lines.append((0, 0, {
                            'name': line.name,
                            'display_type': line.display_type,
                            'description': False,
                            'use_project_task': True,
                            'planned_date_begin': False,
                            'planned_date_end': False,
                            'partner_id': False,
                            'task_timesheet_id': False,
                        }))
                    else:
                        plan_lines.append((0, 0, {
                            'name': line.name,
                            'description': line.description,
                            'use_project_task': True,
                            'planned_date_begin': line.planned_date_begin,
                            'planned_date_end': line.planned_date_end,
                            'partner_id': [(6, 0, line.partner_id.ids)],
                            'task_timesheet_id': line.task_timesheet_id.id,
                            'display_type': False
                        }))

            for line in record.sale_order_id.project_picking_lines:
                if line.display_type == 'line_section':
                    picking_lines.append((0, 0, {
                        'name': line.name,
                        'display_type': line.display_type,
                        'product_id': False,
                        'quantity': False,
                        'standard_price': False,
                        'subtotal': False
                    }))
                else:
                    picking_lines.append((0, 0, {
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'standard_price': line.standard_price,
                        'subtotal': line.subtotal,
                        'display_type': False
                    }))

            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines

    
    def action_confirm_create_project(self):
        self.ensure_one()

        # project_plan_lines_vals = [(0, 0, {
        #     'name': line.name,
        #     'chapter': line.chapter,
        #     'description': line.description,
        #     'use_project_task': line.use_project_task,
        #     'planned_date_begin': line.planned_date_begin,
        #     'planned_date_end': line.planned_date_end,
        #     'task_timesheet_id': line.task_timesheet_id.id,
        #     'partner_id': [(6, 0, line.partner_id.ids)]
        # }) for line in self.wizard_plan_lines if line.use_project_task]

        # picking_lines_vals = [(0, 0, {
        #     'product_id': line.product_id.id,
        #     'quantity': line.quantity,
        # }) for line in self.wizard_picking_lines]

        project_vals = {
            'name': self.project_name,
            'description': self.description,
            'project_plan_lines': [(6, 0, self.wizard_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.wizard_picking_lines.ids)],
        }

        logger.warning(f"project_vals")

        project = self.env['project.project'].create(project_vals)
        self.create_project_tasks(project)

        logger.warning(f"create_project_task")

        self.project_plan_id.project_name = False

        if self.is_sale_order:

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'context': self.env.context
            }
        else:
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

    @api.depends('wizard_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.wizard_picking_lines)