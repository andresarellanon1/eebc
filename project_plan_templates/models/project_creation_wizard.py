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

    picking_type_id = fields.Many2one('stock.picking.type', string="Tipo de operacion")
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    partner_id = fields.Many2one('res.partner', string='Contacto')

    @api.onchange('sale_order_id')
    def _compute_wizard_lines(self):
        for record in self:
            
            record.wizard_picking_lines = [(5, 0, 0)]
            record.wizard_plan_lines = [(5, 0, 0)]

            plan_lines = self.prep_plan_lines(record.sale_order_id.project_plan_lines)
            picking_lines = self.prep_picking_lines(record.sale_order_id.project_picking_lines)

            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines

    
    def action_confirm_create_project(self):
        self.ensure_one()

        project_plan_lines = self.prep_plan_lines(self.sale_order_id.project_plan_lines)
        picking_line_vals = self.prep_picking_lines(self.sale_order_id.project_picking_lines)

        project_vals = {
            'name': self.project_name,
            'description': self.description,
            'project_plan_lines': project_plan_lines,
            'project_picking_lines': picking_line_vals,
        }

        logger.warning(f"project_vals")

        project = self.env['project.project'].create(project_vals)
        self.create_project_tasks(project)

        logger.warning(f"create_project_task")

        self.sale_order_id.state = 'budget'
        self.sale_order_id.project_id = project.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def create_project_tasks_pickings(self, task_id, pickings):
        stock_move_ids_vals = [(0, 0, {
            'product_id': line.product_id.id,
            'product_packaging_id': line.product_packaging_id.id,
            'product_uom_qty': 0,
            'quantity': line.quantity,
            'product_uom': line.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'name': task_id.name
        }) for line in pickings]

        stock_picking_vals = {
            'name': task_id.name,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id,
            'location_id': self.location_id.id,
            'scheduled_date': self.scheduled_date,
            'origin': task_id.name,
            'task_id': task_id.id,
            'user_id': self.env.user.id,
            'move_ids': stock_move_ids_vals,
            'carrier_id': False,
            'carrier_tracking_ref': False,
            'weight': False,
            'shipping_weight': False,
            'company_id': self.env.company.id,
            'transport_type': False,
            'custom_document_identification': False,
            'lat_origin': False,
            'long_origin': False,
            'lat_det': False,
            'long_dest': False,
            'note': False
        }

        self.env['stock.picking'].create(stock_picking_vals)

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

                task_id = self.env['project.task'].create({
                    'name': line.name,
                    'project_id': project.id,
                    'stage_id': current_task_type.id,
                    'user_ids': line.partner_id.ids,
                    'timesheet_ids': timesheet_data,
                })

                self.create_project_tasks_pickings(task_id, line.project_plan_pickings.project_picking_lines)

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

    def prep_plan_lines(self, plan):
        plan_lines = []
        for line in plan:
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
                        'project_plan_pickings': False,
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
                        'project_plan_pickings' line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                        'display_type': False
                    }))
        return plan_lines

    def prep_picking_lines(self, picking):
        picking_lines = []
        for line in picking:
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
        return picking_lines

    @api.depends('wizard_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.wizard_picking_lines)