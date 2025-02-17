from odoo import fields, models, api
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class ProjectVersionWizard(models.TransientModel):

    _name = 'project.version.wizard'
    _description = 'Wizard for project version history'

    modification_date = fields.Datetime(string='Fecha de modificación')
    modification_motive = fields.Html(string='Motivo de los cambios')
    modified_by = fields.Many2one('res.users', string='Modificado por', required=True)
    plan_total_cost = fields.Float(string="Costo total",  compute='_compute_total_cost', default=0.0)

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación'
    )
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Inventario'
    )

    wizard_plan_lines = fields.One2many(
        'project.plan.wizard.line', 'wizard_version_id',
        string="Project Plan Lines"
    )

    wizard_picking_lines = fields.One2many(
        'project.picking.wizard.line', 'wizard_version_history_id',
        string="Project Picking Lines"
    )

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada de entrega')
    contact_id = fields.Many2one('res.partner', string='Contacto')
    date_start = fields.Datetime(string="Fecha de inicio planeada")
    picking_type_id = fields.Many2one('stock.picking.type', string="Tipo de operacion")
    date = fields.Datetime()
    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")

    # This action confirms and records changes in the project's version history.
    # It ensures the existence of a project version history, creates one if none exists, 
    # validates that a modification reason is provided, and raises an error if it's missing.
    # The method generates tasks for the project using `create_project_tasks` from the `project.project` model.
    # Afterward, it creates a new entry in the version history with the current modification details.
    # Finally, it saves the updated project information and closes the wizard window.

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

    @api.onchange('sale_order_id')
    def _compute_wizard_lines(self):
        for record in self:
            record.project_picking_lines = [(5, 0, 0)]
            record.project_plan_lines = [(5, 0, 0)]

            plan_lines = self.prep_plan_lines(record.sale_order_id.project_plan_lines)
            picking_lines = self.prep_picking_lines(record.sale_order_id.project_picking_lines)

            record.wizard_plan_lines = plan_lines
            record.wizard_picking_lines = picking_lines

    def action_confirm_version_history(self):
        self.ensure_one()

        project = self._origin.project_id
        if not project:
            raise ValueError("No se encontró el proyecto asociado.")

        project.actual_sale_order_id = self.sale_order_id.id
        project.sale_order_id = self.sale_order_id.id

        existing_plan_lines = self.prep_plan_lines(project.project_plan_lines)
        new_plan_lines_data = self.prep_plan_lines(self.sale_order_id.project_plan_lines)

        project.project_plan_lines = [
            (1, line[1], new_line[2]) if line[2]['name'] == new_line[2]['name'] else (4, line[1])
            for line in existing_plan_lines
            for new_line in new_plan_lines_data
            if line[2]['name'] == new_line[2]['name']
        ] + [
            new_line for new_line in new_plan_lines_data
            if all(new_line[2]['name'] != line[2]['name'] for line in existing_plan_lines)
        ]

        existing_picking_lines = self.prep_picking_lines(project.project_picking_lines)
        new_picking_lines_data = self.prep_picking_lines(self.sale_order_id.project_picking_lines)

        project.project_picking_lines = [
            (1, line[1], new_line[2]) if line[2]['name'] == new_line[2]['name'] else (4, line[1])
            for line in existing_picking_lines
            for new_line in new_picking_lines_data
            if line[2]['name'] == new_line[2]['name']
        ] + [
            new_line for new_line in new_picking_lines_data
            if all(new_line[2]['name'] != line[2]['name'] for line in existing_picking_lines)
        ]

        project.write({})

        # Check if a version history already exists for the current project.
        existing_history = self.env['project.version.history'].search([('project_id', '=', self.project_id.id)], limit=1)

        # If no version history exists, create a new one.
        if not existing_history:
            history = self.env['project.version.history'].create({
                'project_id': self.project_id.id,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
                'project_name': self.project_id.name,
            })
        else:
            history = existing_history  # Use the existing history if found.

        # Ensure that a modification motive is provided; raise an error if missing.
        if not self.modification_motive:
            raise UserError(f'Hace falta agregar el motivo de la modificación.')

        # Create any newly added tasks for the project.
        project.create_project_tasks(self.location_id.id, self.location_dest_id.id, self.scheduled_date)

        # for sale in self.sale_order_id.project_picking_lines:
        #     sale.for_modification = False

        # Create a new entry in the project version lines for the modification details.
        self.env['project.version.lines'].create({
            'project_version_history_id': history.id,
            'modification_date': self.modification_date,
            'modified_by': self.modified_by.id,
            'modification_motive': self.modification_motive,
            'project_plan_lines': [(6, 0, self.sale_order_id.project_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.sale_order_id.project_picking_lines.ids)],
        })

        # Eliminar duplicados después de la modificación
        self.sale_order_id.clean_duplicates_after_modification()
        self.sale_order_id.state = 'sale'
        # Close the wizard window after completing the action.
        return {
            'type': 'ir.actions.act_window_close'
        }

    def prep_plan_lines(self, plan):
        plan_lines = []
        for line in plan:
            if line.use_project_task:
                if line.display_type == 'line_section':
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'sequence': line.sequence,
                        'display_type':  line.display_type or 'line_section',
                        'description': False,
                        'use_project_task': True,
                        'planned_date_begin': False,
                        'planned_date_end': False,
                        'project_plan_pickings': False,
                        'task_timesheet_id': False,
                        'for_create': line.for_create
                    }))
                else:
                    plan_lines.append((0, 0, {
                        'name': line.name,
                        'sequence': line.sequence,
                        'description': line.description,
                        'use_project_task': True,
                        'planned_date_begin': line.planned_date_begin,
                        'planned_date_end': line.planned_date_end,
                        'project_plan_pickings': line.project_plan_pickings.id,
                        'task_timesheet_id': line.task_timesheet_id.id,
                        'display_type': False,
                        'for_create': True
                    }))
        return plan_lines

    def prep_picking_lines(self, picking):
        picking_lines = []
        for line in picking:
            if line.display_type == 'line_section':
                picking_lines.append((0, 0, {
                    'name': line.name,
                    'sequence': line.sequence,
                    'display_type': line.display_type or 'line_section',
                    'product_id': False,
                    'product_uom': False,
                    'product_packaging_id': False,
                    'product_uom_qty': False,
                    'quantity': False,
                    'standard_price': False,
                    'subtotal': False
                }))
            else:
                picking_lines.append((0, 0, {
                    'name': line.product_id.name,
                    'sequence': line.sequence,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_packaging_id': line.product_packaging_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'quantity': line.quantity,
                    'standard_price': line.standard_price,
                    'subtotal': line.subtotal,
                    'display_type': False
                }))
        return picking_lines
