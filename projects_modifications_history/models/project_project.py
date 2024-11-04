from odoo import models, api, fields
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    redirect_view_id = fields.Many2one('ir.ui.view', string='Redirect View', default=lambda self: self.env.ref('your_module.your_view_id'))

    version_history_ids = fields.One2many(
        'project.version.history', 
        'project_id', 
        string='Historial de modificaciones',
        readonly=True,
    )

    # This action opens a wizard to generate a new version entry in the project's change history.
    # The wizard allows users to review the project plan lines (tasks to be created or added)
    # and the products included in the project's inventory. Additionally, it records the reason
    # for the changes as the most crucial information.
    # The context provides default values for the wizard, including:
    # - 'default_project_id': the current project's ID
    # - 'default_project_plan_id': the ID of the project plan
    # - 'default_project_plan_lines': the IDs of the project plan lines (tasks)
    # - 'default_project_picking_lines': the IDs of the project's inventory products
    # - 'default_modified_by': the current user making the modifications
    # - 'default_modification_date': the date and time of the modification

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