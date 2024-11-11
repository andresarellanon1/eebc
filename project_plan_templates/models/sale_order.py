from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        self.ensure_one()
        products_ids = []

        for line in self.order_line:
            if line.product_template_id.detailed_type == 'service':
                if line.product_template_id.service_tracking == 'project_only':
                    products_ids.append(line.product_template_id.id)

        super(SaleOrder, self).action_confirm()

        return {
            'name': 'Projects creation',
            'view_mode': 'form',
            'res_model': 'project.sale.creation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_products_ids': [(6, 0, products_ids)]
            }
        }

