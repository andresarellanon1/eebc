from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_id = fields.Many2one('project.version', string="History")
    change_motive = fields.Text(string='Motivo')

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
        new_context = dict(self.env.context) # Crear un nuevo contexto en lugar de modificar el existente
        new_context['vals'] = vals  # Almacenar los valores en el nuevo contexto
       
        # Llama al wizard antes de guardar
        if vals:
            new_context['active_id'] = self.id
            wizard = self.env['change.reason.wizard'].create({})
            return {
                'name': 'Change Reason',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'change.reason.wizard',
                'type': 'ir.actions.act_window',
                'context': new_context,
                'target': 'new',  # Abrir en popup
                'res_id': wizard.id,
            }

        # Se guarda el estado actual antes de modificar
        project_version = self.env['project.version']
        for project in self:
            project_version.create_version(project, self.env.user)

        # Se modifica
        return super(ProjectProject, self).write(vals)

    # @api.depends('project_plan_id','project_plan_description','project_plan_lines')
    # def _onchange_plan_template():