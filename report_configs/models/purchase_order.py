from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('report_configs.out_purchaseorder_template_custom').report_action(self)


    def _get_name_invoice_report(self):
        self.ensure_one()
        return 'report_configs.out_purchaseorder_template_custom'