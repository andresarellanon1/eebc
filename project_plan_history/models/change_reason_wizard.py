from odoo import models, fields, api

class ChangeReasonWizard(models.TransientModel):
    _name = 'change.reason.wizard'
    _description = 'Change Reason Wizard'

    motive = fields.Text(string='Motivo')

    def confirm(self):
        project_id = self.env.context.get('active_id')
        if project_id:
            project = self.env['project.project'].browse(project_id)
            project.change_motive = self.reason  # Guardar el motivo en el registro
            
            # Crear la versión solo después de confirmar
            project_version = self.env['project.version']
            project_version.create_version(project, self.env.user)

            # Ahora se realizan los cambios
            return project.write(self.env.context.get('vals', {}))
        return {'type': 'ir.actions.act_window_close'}