from odoo import models, api, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        for record in self:
            wizard = self.env['project.version.wizard'].create({
                'modification_date': fields.Datetime.now(),
                'modified_by': self.env.user.id,
                'project_plan_lines': [(6, 0, [line.id for line in record.project_plan_lines])],
                'project_picking_lines': [(6, 0, [line.id for line in record.project_picking_lines])],
            })

            return {
                'name': 'Project Version History',
                'view_mode': 'form',
                'res_model': 'project.version.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_project_id': record.id
                }
            }

        return super(ProjectProject, self).write(vals)