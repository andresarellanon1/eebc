from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class ProjectSaleWizard(models.TransientModel):

    _name = 'project.sale.creation.wizard'
    _description = 'Wizard to create projects from sale order'

    products_ids = fields.Many2many('product.template')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)

    def confirm_wizard(self):
        self.ensure_one()

        project_plan = self.project_plan_id

        if self.products_ids == 1:
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
                    'default_project_name': self.products_ids[0].name
                }
            }
        else:
            raise ValidationError(
                        f"Only one service is allowed per sale order."
                    )

        self.sale_order_id.state = 'sale'