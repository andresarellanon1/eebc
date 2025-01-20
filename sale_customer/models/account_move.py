import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_reference = fields.Char(string="Orden de compra", help="Referencia de la orden de compra del cliente. Este campo no representa una orden de compra dentro de odoo. Se refiere a una orden de compra en el sistema del cliente.")

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            line_order_references = set()  # Use a set to avoid duplicates
            for line in move.line_ids:
                source_order_customer_reference = line.sale_line_ids.order_id.customer_reference
                if source_order_customer_reference:
                    line_order_references.add(source_order_customer_reference)  # Add to the set

            move.customer_reference = ','.join(line_order_references)
        return moves

    # get the correct name for the report of invoice
    # def _get_name_invoice_report(self):
    #     self.ensure_one()
    #     if self.move_type in ['out_invoice', 'out_refund']:
    #         return 'morvil_report_invoice.morvil_out_invoice_template'
    #     else:
    #         return 'account.report_invoice_document'
