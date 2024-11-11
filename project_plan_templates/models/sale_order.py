from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        for line in self.order_line:
            if line.product_template_id.detailed_type == 'service':
                if line.product_template_id.service_tracking == 'project_only':
                    line.product_template_id.use_for_project = True