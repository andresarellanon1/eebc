from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    project_plan_id = fields.Many2one('project.plan', string="Project plan template")
    
    @api.constrains('project_plan_id')
    def _check_unique_project_plan_per_service(self):
        for record in self:
            if record.project_plan_id:
                duplicate = self.env['product.template'].search([
                    ('project_plan_id', '=', record.project_plan_id.id),
                    ('id', '!=', record.id),
                    ('type', '=', 'service')  
                ])
                if duplicate:
                    raise ValidationError((
                        "El plan de proyecto '%s' ya está asignado a otro servicio. "
                        "No puede haber más de un servicio con el mismo plan de proyecto."
                    ) % record.project_plan_id.display_name)
