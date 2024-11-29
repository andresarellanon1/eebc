from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_plan_id = fields.Many2one(
        'project.plan',
        string="Plantilla de proyecto",
        ondelete='restrict',  
    )

    @api.constrains('project_plan_id')
    def _check_unique_project_plan(self):
        for record in self:
            if record.project_plan_id:
                duplicates = self.search([('project_plan_id', '=', record.project_plan_id.id), ('id', '!=', record.id)])
                if duplicates:
                    raise ValidationError("El proyecto '%s' ya está asignado a otro producto." % record.project_plan_id.display_name)

    @api.model
    def write(self, vals):
        if 'project_plan_id' in vals and vals['project_plan_id']:
            plan = self.env['project.plan'].browse(vals['project_plan_id'])
            if plan:
                plan.write({'product_template_id': self.id})
        else:
            if self.project_plan_id.product_template_id:
                self.project_plan_id.product_template_id = False 
                self.project_plan_id = False  # Elimina la referencia
        result = super(ProductTemplate, self).write(vals)
        return result