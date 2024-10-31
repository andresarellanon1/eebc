from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_id = fields.Many2one('project.version', string="History")
    change_reason = fields.Text(string="Motivo")
    cambio = fields.Boolean(default=False)

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
        self.abrir_wizard()
        
        project_version = self.env['project.version']
        for project in self:
            project_version.create_version(project, self.env.user)
        
        return super(ProjectProject, self).write(vals)

    def abrir_wizard(self):
        _logger.warning('Entró al metodo del wizard')
        cambio = True

    @api.onchange('cambio')
    def metodo2(self):
        _logger.warning('Entró al metodo del CAMBIO')

    

        return wizard
        # self.ensure_one()
        # return {
        #     'name': 'Mi Wizard',
        #     'view_mode': 'form',
        #     'res_model': 'change.reason.wizard',
        #     'type': 'ir.actions.act_window',
        #     'view_id': 'view_change_reason_wizard',
        #     'target': 'new',  # Esto abre el wizard en un modal
        # }

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
    #             'motive': 'change_reason'
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
