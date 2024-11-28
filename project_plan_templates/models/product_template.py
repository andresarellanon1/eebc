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
        result = super(ProductTemplate, self).write(vals)
        if 'project_plan_id' in vals and vals['project_plan_id']:
            plan = self.env['project.plan'].browse(vals['project_plan_id'])
            if plan:
                plan.write({'product_template_id': self.id})
        else:
            for record in self:
                plan = self.env['project.plan'].search([
                    ('product_template_id', '=', record.id),
                ])
                plan.write({'product_template_id': False})
        return result