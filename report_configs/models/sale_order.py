from odoo import fields, models, api

class sale_order(models.Model):

    _inherit = 'sale.order'

    def _get_name_sale_report(self):
        self.ensure_one()
        return 'report_configs.out_saleorder_template_custom'