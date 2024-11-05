import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProjectVersionWizard(models.TransientModel):
    _name = 'project.version.wizard'
    _description = 'Wizard for project version history'

    modification_date = fields.Datetime(string='Modification date')
    modification_motive = fields.Html(string='Motive of adjustment')
    modified_by = fields.Many2one('res.users', string='Modified by', required=True)

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación'
    )
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock'
    )

    project_id = fields.Many2one('project.project', string='Project', required=True)

    def action_confirm_version_history(self):
        self.ensure_one()

        # Logger para verificar el ID del proyecto
        _logger.info("Project ID: %s", self.project_id)

        project = self.env['project.project'].browse(self.project_id.id)

        # Logger para ver si se encuentra historial existente
        _logger.info("Searching for existing history with Project ID: %s", self.project_id.id)

        existing_history = self.env['project.version.history'].search([
            ('project_id', '=', self.project_id.id)
        ], limit=1)

        if not existing_history:
            _logger.info("No existing history found, creating new one.")
            history = self.env['project.version.history'].create({
                'project_id': self.project_id.id,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
                'project_name': self.project_id.name,
            })
        else:
            _logger.info("Existing history found with ID: %s", existing_history.id)
            history = existing_history

        if not self.modification_motive:
            raise UserError('Hace falta agregar el motivo de la modificacion.')

        # Logger para la creación de tareas del proyecto
        _logger.info("Creating project tasks for Project ID: %s", self.project_id.id)
        project.create_project_tasks()

        # Logger para verificar las líneas seleccionadas en project_plan_lines y project_picking_lines
        _logger.info("Plan lines IDs: %s", self.project_plan_lines.ids)
        _logger.info("Picking lines IDs: %s", self.project_picking_lines.ids)

        self.env['project.version.lines'].create({
            'project_version_history_id': history.id,
            'modification_date': self.modification_date,
            'modified_by': self.modified_by.id,
            'modification_motive': self.modification_motive,
            'project_plan_lines': [(6, 0, self.project_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.project_picking_lines.ids)],
        })

        _logger.info("Version history saved successfully for Project ID: %s", self.project_id.id)

        return {
            'type': 'ir.actions.act_window_close'
        }