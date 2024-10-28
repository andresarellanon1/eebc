from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    version_id = fields.Many2one('project.version', string="History")
    change_motive = fields.Text(string='Change Reason')

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
         # Guardamos los valores en el contexto para poder usarlos más tarde
        self.env.context['vals'] = vals
        
        # Llama al wizard antes de guardar
        if vals:
            context = dict(self.env.context)
            context['active_id'] = self.id
            wizard = self.env['change.reason.wizard'].create({})
            return {
                'name': 'Change Reason',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'change.reason.wizard',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new',  # Abrir en popup
                'res_id': wizard.id,
            }

        # Se modifica
        return super(ProjectProject, self).write(vals)

    # @api.depends('project_plan_id','project_plan_description','project_plan_lines')
    # def _onchange_plan_template():

