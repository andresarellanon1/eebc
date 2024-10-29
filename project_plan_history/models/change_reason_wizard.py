from odoo import models, fields, api

class ChangeReasonWizard(models.TransientModel):
    _name = 'change.reason.wizard'
    _description = 'Change Reason Wizard'

    motive = fields.Text(string='Motivo')

    def confirm(self):
        project_id = self.env.context.get('active_id')

        # Se guarda el estado actual antes de modificar
        project_version = self.env['project.version']

        for project in self:
            project_version.create_version(project, self.env.user)
            
        if project_id:
            project = self.env['project.project'].browse(project_id)
            project.change_motive = self.reason  # Guardar el motivo en el registros
        return {'type': 'ir.actions.act_window_close'}