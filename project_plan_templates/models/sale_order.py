from odoo import fields, models, api
import json

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Is project?", default=False)
    project_name = fields.Char(string="Project title")
    state = fields.Selection(
        selection_add=[
            ('estimation', 'Estimation')
        ],
        ondelete={
            'estimation': 'set default'
        }
    )
    products_template_domain = fields.Char(string="products_domain", compute="_compute_product_domain", store=True)

    @api.depends('is_project')
    def _compute_product_domain(self):
        for record in self:
            if(record.is_project):
                products = self.env['project.template'].search([('detailed_type', '=', 'service')])
                record.products_template_domain = json.dumps([('id', 'in', products.ids)])

    def action_confirm(self):
        self.ensure_one()
         # Initialize empty lists to separate service products and other products
        services_ids = []
        products_ids = []

        # Loop through each line in the sales order
        for line in self.order_line:
            # Check if the product type is 'service'
            if line.product_template_id.detailed_type == 'service':
                # Check if the service requires a project (tracking mode is 'project_only')
                if line.product_template_id.service_tracking == 'project_only':
                    # Ensure the service product has a project plan associated with it
                    if line.product_template_id.project_plan_id:
                        # Add the service product template ID to the services list
                        services_ids.append(line.product_template_id.id)
            else:
                # If not a service or doesn't meet the conditions, add to products list
                products_ids.append(line.product_template_id.id)

        # If there are any service products that require a project
        if services_ids:
            # Open the project creation wizard and pass the necessary context
            return {
                'name': 'Projects creation',  # Wizard title
                'view_mode': 'form',  # Display mode for the wizard
                'res_model': 'project.sale.creation.wizard',  # Model for the wizard
                'type': 'ir.actions.act_window',  # Action type to open a new window
                'target': 'new',  # Open in a modal ('new' window)
                'context': {
                    'default_services_ids': [(6, 0, services_ids)],  # Pass service IDs to wizard
                    'default_products_ids': [(6, 0, products_ids)],  # Pass other product IDs
                    'default_sale_order_id': self.id  # Pass the current sale order ID
                }
            }
        else:
            # If no service products require a project, proceed with the default action
            return super(SaleOrder, self).action_confirm()
            