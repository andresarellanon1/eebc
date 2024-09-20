from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    def _get_name_purchase_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'