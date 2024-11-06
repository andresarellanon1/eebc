from odoo import models, api, fields
import logging

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_history_ids = fields.One2many(
        'project.version.history',
        'project_id',
        string='Historial de modificaciones',
        readonly=True,
    )

    version_history_id = fields.Many2one(
        'project.version.history',
        string='Version History',
        compute='_compute_version_history_id',
        store=True
    )

    @api.depends('version_history_ids')
    def _compute_version_history_id(self):
        for project in self:
            version_history = self.env['project.version.history'].search([('project_id', '=', project.id)], limit=1)
            project.version_history_id = version_history if version_history else False

    def action_save_version(self):
        self.ensure_one()

        _logger = logging.getLogger(__name__)

        _logger.info("Valor de project_plan_id: %s", self.project_plan_id)
        _logger.info("Valor de project_plan_lines: %s", self.project_plan_lines)
        _logger.info("Valor de project_picking_lines: %s", self.project_picking_lines)

        return {
            'name': 'Project Version History',
            'view_mode': 'form',
            'res_model': 'project.version.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_project_plan_id': self.project_plan_id.id if self.project_plan_id else False,
                'default_project_plan_lines': [(6, 0, self.project_plan_lines.ids)] if self.project_plan_lines else False,
                'default_project_picking_lines': [(6, 0, self.project_picking_lines.ids)] if self.project_picking_lines else False,
                'default_modified_by': self.env.user.id,
                'default_modification_date': fields.Datetime.now(),
            }
        }