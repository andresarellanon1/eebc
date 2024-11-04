from odoo import models, api, fields
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # NO SE USA PERO ME DA ERROR SI LO QUITO
    redirect_view_id = fields.Many2one('ir.ui.view', string='Redirect View', default=lambda self: self.env.ref('your_module.your_view_id'))
    version_history_ids = fields.One2many(
        'project.version.history', 
        'project_id', 
        string='Historial de modificaciones',
        readonly=True,
    )

    def action_view_modifications_history(self):
        "empty"

    def action_save_version(self):
        self.ensure_one()

        return {
            'name': 'Project Version History',
            'view_mode': 'form',
            'res_model': 'project.version.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_project_plan_id': self.project_plan_id.id,
                'default_project_plan_lines': [(6, 0, self.project_plan_lines.ids)],
                'default_project_picking_lines': [(6, 0, self.project_picking_lines.ids)],
                'default_modified_by': self.env.user.id,
                'default_modification_date': fields.Datetime.now(),
            }
        }