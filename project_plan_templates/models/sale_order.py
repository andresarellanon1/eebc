from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        self.ensure_one()
        products_ids = []

        for line in self.order_line:
            if line.product_template_id.detailed_type == 'service':
                if line.product_template_id.service_tracking == 'project_only':
                    if line.product_template_id.project_plan_id:
                        products_ids.append(line.product_template_id.id)

        if products_ids:
            return {
                'name': 'Projects creation',
                'view_mode': 'form',
                'res_model': 'project.sale.creation.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_products_ids': [(6, 0, products_ids)],
                    'default_sale_order_id': self.id
                }
            }
        else:
            return super(SaleOrder, self).action_confirm()