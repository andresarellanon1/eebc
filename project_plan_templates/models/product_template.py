from odoo import fields, models, api
from odoo.exceptions import ValidationError

# Extends the product.template model to include project plan template association
# and implements unique project plan validation for service products.
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    project_plan_id = fields.Many2one('project.plan', string="Project plan template")

    # Validates that a project plan template is uniquely assigned to a service product.
    # Prevents multiple service products from being associated with the same project plan.
    # Raises a ValidationError if a duplicate is found.
    @api.constrains('project_plan_id')
    def _check_unique_project_plan_per_service(self):
        for record in self:
            if record.project_plan_id:
                # Search for duplicate service products with the same project plan
                duplicate = self.env['product.template'].search([
                    ('project_plan_id', '=', record.project_plan_id.id),  
                    ('id', '!=', record.id),  
                    ('type', '=', 'service') 
                ])
                
                # Raise validation error if duplicate found
                if duplicate:
                    raise ValidationError((
                        "El plan de proyecto '%s' ya está asignado a otro servicio. "
                        "No puede haber más de un servicio con el mismo plan de proyecto."
                    ) % record.project_plan_id.display_name)

    @api.model
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'project_plan_id' in vals:
            for record in self:
                if record.project_plan_id:
                    record.project_plan_id.product_template_ids = [(4, record.id)]
        return res
