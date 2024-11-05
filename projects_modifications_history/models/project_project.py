import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Definición de campos necesarios si aún no están definidos
    project_plan_id = fields.Many2one('project.plan', string='Project Plan')
    project_plan_lines = fields.One2many('project.plan.line', 'project_id', string='Plan Lines')
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string='Picking Lines')

    def action_save_version(self):
        self.ensure_one()

        # Loggers para verificar los valores antes de pasarlos al wizard
        _logger.info("Project ID: %s", self.id)
        _logger.info("Project Plan ID: %s", self.project_plan_id.id if self.project_plan_id else 'No plan')
        _logger.info("Project Plan Lines: %s", self.project_plan_lines.ids)
        _logger.info("Project Picking Lines: %s", self.project_picking_lines.ids)

        return {
            'name': 'Project Version History',
            'view_mode': 'form',
            'res_model': 'project.version.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                # Asegura que el valor sea False si no existe project_plan_id
                'default_project_plan_id': self.project_plan_id.id if self.project_plan_id else False,
                # Asegura que el campo acepte una lista vacía si no hay líneas
                'default_project_plan_lines': [(6, 0, self.project_plan_lines.ids)] if self.project_plan_lines else [(6, 0, [])],
                'default_project_picking_lines': [(6, 0, self.project_picking_lines.ids)] if self.project_picking_lines else [(6, 0, [])],
                'default_modified_by': self.env.user.id,
                'default_modification_date': fields.Datetime.now(),
            }
        }
