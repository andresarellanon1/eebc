from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    @api.print_quotation
    def _get_name_invoice_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'