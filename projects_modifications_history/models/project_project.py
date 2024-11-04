from odoo import models, api, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def action_view_modifications_history(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Modifications History',
            'res_model': 'project.version.history',
            'view_mode': 'form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

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