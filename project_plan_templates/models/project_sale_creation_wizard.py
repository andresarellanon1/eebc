from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

# Wizard model for creating projects from sale orders. This wizard handles
# the selection of products and services from a sale order, validates the
# configuration, and creates a project based on a project plan template.
class ProjectSaleWizard(models.TransientModel):
   _name = 'project.sale.creation.wizard'
   _description = 'Wizard to create projects from sale order'

   # Selection fields for products and services
   products_ids = fields.Many2many('product.template', 'wizard_product_template_rel',)
   services_ids = fields.Many2many('product.template', 'wizard_service_template_rel',)
   
   # Reference fields
   sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
   project_plan_id = fields.Many2one('project.plan', string="Project plan template")

   # This method processes the wizard confirmation and creates a project.
   # It performs the following steps:
   # - Validates that only one service is selected
   # - Gets the project plan template from the selected service
   # - Removes sale order lines for non-selected products
   # - Updates sale order state
   # - Opens project creation wizard with pre-filled values
   # Raises:
   #   ValidationError: If more than one service is selected
   def confirm_wizard(self):
       self.ensure_one()

       if len(self.services_ids) == 1:
           service = self.services_ids[0] 
           project_plan = service.project_plan_id

           # Filter allowed products and remove other lines
           allowed_product_ids = (self.products_ids + self.services_ids).mapped('id')
           lines_to_remove = self.sale_order_id.order_line.filtered(
               lambda line: line.product_id.product_tmpl_id.id not in allowed_product_ids
           )
           lines_to_remove.unlink()
           
           # Update sale order state
           self.sale_order_id.state = 'sale'

           # Open project creation wizard with default values
           return {
               'name': 'Create Project',
               'view_mode': 'form',
               'res_model': 'project.creation.wizard',
               'type': 'ir.actions.act_window',
               'target': 'new',
               'context': {
                   'default_project_plan_id': project_plan,
                   'default_project_plan_lines': [(6, 0, project_plan.project_plan_lines.ids)],
                   'default_project_plan_pickings': [(6, 0, project_plan.project_plan_pickings.ids)],
                   'default_picking_lines': [(6, 0, project_plan.picking_lines.ids)],
                   'default_description': project_plan.description,
                   'default_is_sale_order': True,
                   'default_project_name': self.services_ids[0].name,
                   'default_sale_order_id': self.sale_order_id.id
               }
           }
       else:
           raise ValidationError(
               f"Only one service is allowed per sale order."
           )