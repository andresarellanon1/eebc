from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_id = fields.Many2one('project.version', string="History")

    child_ids = fields.One2many(
        'project.project',
        'parent_id',
        string="Subprojects"
    )
    
    parent_id = fields.Many2one(
        'project.project',
        string="Parent Project",
        ondelete='set null'
    )

    @api.model
    def write(self, vals):
        result = super(ProjectProject, self).write(vals)
        project_version = self.env['project.version']
        for project in self:
            project_version.create_version(project, self.env.user)
        
        return result

    # def abrir_wizard(self):
    #     return {
    #         'name': 'Mi Wizard',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'change.reason.wizard',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'target': 'new',  # Esto abre el wizard en un modal
    #     }

    # @api.model
    # def write(self, vals):
    #     # Crear una versión del proyecto antes de modificarlo
    #     project_version = self.env['project.version']
    #     for project in self:
    #         project_version.create_version(project, self.env.user)
    
    #     # Llamar al wizard
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'project.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_field1': 'Valor inicial de Field 1',
    #             'default_field2': 10,
    #         },
    #     }


    #  # Crear un nuevo contexto en lugar de modificar el existente
    #     new_context = dict(self.env.context)
    #     new_context['vals'] = vals  # Almacenar los valores en el nuevo contexto
        
    #     # Llama al wizard antes de guardar
    #     if vals:
    #         new_context['active_id'] = self.id
    #         wizard = self.env['change.reason.wizard'].create({})
    #         return {
    #             'name': 'Change Reason',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'change.reason.wizard',
    #             'type': 'ir.actions.act_window',
    #             'context': new_context,
    #             'target': 'new',  # Abrir en popup
    #             'res_id': wizard.id,
    #         }
