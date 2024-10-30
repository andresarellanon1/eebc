from odoo import models, api, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def write(self, vals):
        wizard = self.env['project.version.wizard'].create({
            'modification_date': fields.Datetime.now(),
            'modified_by': self.env.user.id,
            'project_plan_lines': [(6, 0, [line.id for line in self.project_plan_lines])],
            'project_picking_lines': [(6, 0, [line.id for line in self.project_picking_lines])],
        })

        return {
            'name': 'Project Version History',
            'view_mode': 'form',
            'res_model': 'project.version.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_id': self.id
            }
        }