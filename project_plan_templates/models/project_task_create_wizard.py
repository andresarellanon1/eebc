from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProjectTaskCreateWizard(models.TransientModel):
    _name = 'project.task.create.wizard'
    _description = 'Wizard para crear una tarea sin duplicados'

    name = fields.Char("Nombre de la Tarea", required=True)
    project_id = fields.Many2one('project.project', string="Proyecto", required=True)

    def action_create_task(self):
        duplicate_task = self.env['project.task'].search([
            ('name', '=', self.name),
            ('project_id', '=', self.project_id.id)
        ], limit=1)

        if duplicate_task:
            raise UserError(_("Ya existe una tarea con el nombre '%s' en este proyecto. Por favor, elige otro nombre.") % self.name)

        self.env['project.task'].create({
            'name': self.name,
            'project_id': self.project_id.id,
        })