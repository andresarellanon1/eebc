from odoo import fields, models, api
from odoo.exceptions import ValidationError

# Extends the product.template model to include project plan template association
# and implements unique project plan validation for service products.
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_plan_id = fields.Many2one(
        'project.plan',
        string="Plantilla de proyecto",
        ondelete='restrict',  # Evita borrar accidentalmente el proyecto
        inverse_name='product_template_id'
    )

    # Validates that a project plan template is uniquely assigned to a service product.
    # Prevents multiple service products from being associated with the same project plan.
    # Raises a ValidationError if a duplicate is found.
    @api.constrains('project_plan_id')
    def _check_unique_project_plan(self):
        for record in self:
            if record.project_plan_id:
                duplicates = self.search([
                    ('project_plan_id', '=', record.project_plan_id.id),
                    ('id', '!=', record.id)
                ])
                if duplicates:
                    raise ValidationError(
                        "El proyecto '%s' ya está asignado a otro producto." % record.project_plan_id.display_name
                    )

    @api.model
    def write(self, vals):
        result = super(ProductTemplate, self).write(vals)
        for record in self:
            if 'project_plan_id' in vals and record.project_plan_id:
                record.project_plan_id.write({'product_template_id': record.id})
        return result