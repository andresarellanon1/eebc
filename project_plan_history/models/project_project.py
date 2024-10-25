from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_ids = fields.One2many('project.version', 'project_id', string='History')

    @api.model
    def write(self, vals):
        # Se guarda el estado actual antes de modificar
        project_version = self.env['project.version']
        for project in self:
            project_version.create_version(project, self.env.user)

        # Se modifica
        return super(ProjectProject, self).write(vals)

    # @api.depends('project_plan_id','project_plan_description','project_plan_lines')
    # def _onchange_plan_template():
