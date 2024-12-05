from odoo import models, fields, api

class ChangeReasonWizard(models.TransientModel):
    _name = 'change.reason.wizard'
    _description = 'Change Reason Wizard'

    motive = fields.Text(string='Motivo')

    def confirm(self):
        project_id = self.env.context.get('active_id')
        if project_id:
            project = self.env['project.project'].browse(project_id)
            project.change_motive = self.motive  # Guardar el motivo en el registro
        return {'type': 'ir.actions.act_window_close'}