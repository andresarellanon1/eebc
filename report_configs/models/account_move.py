from odoo import fields, models, api

class AccountMove(models.Model):

    _inherit = 'account.move'

    def _get_name_invoice_report(self):
        self.ensure_one()
        return 'report_configs.out_invoice_template_custom'