import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_cost = fields.Float('Costo total', compute="_compute_sale_cost", store=False)

    @api.depends('invoice_line_ids', 'pre_invoice', 'is_government', 'material_change')
    def _compute_sale_cost(self):
        for move in self:
            cost = 0.00
            for line in move.invoice_line_ids:
                cost += line.sale_unit_cost * line.quantity
            move.sale_cost = cost

    # def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
    #     ''' Prepare values used to create the journal items (account.move.line) corresponding to the Cost of Good Sold
    #     lines (COGS) for customer invoices.
    #
    #     Example:
    #
    #     Buy a product having a cost of 9 being a storable product and having a perpetual valuation in FIFO.
    #     Sell this product at a price of 10. The customer invoice's journal entries looks like:
    #
    #     Account                                     | Debit | Credit
    #     ---------------------------------------------------------------
    #     200000 Product Sales                        |       | 10.0
    #     ---------------------------------------------------------------
    #     101200 Account Receivable                   | 10.0  |
    #     ---------------------------------------------------------------
    #
    #     This method computes values used to make two additional journal items:
    #
    #     ---------------------------------------------------------------
    #     220000 Expenses                             | 9.0   |
    #     ---------------------------------------------------------------
    #     101130 Stock Interim Account (Delivered)    |       | 9.0
    #     ---------------------------------------------------------------
    #
    #     Note: COGS are only generated for customer invoices except refund made to cancel an invoice.
    #
    #     :return: A list of Python dictionary to be passed to env['account.move.line'].create.
    #     '''
    #     lines_vals_list = []
    #     price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
    #     for move in self:
    #         # Make the loop multi-company safe when accessing models like product.product
    #         move = move.with_company(move.company_id)
    #
    #         if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
    #             continue
    #
    #         for line in move.invoice_line_ids:
    #
    #             # Filter out lines being not eligible for COGS.
    #             if not line._eligible_for_cogs():
    #                 continue
    #
    #             # Retrieve accounts needed to generate the COGS.
    #             accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
    #             debit_interim_account = accounts['stock_output']
    #             credit_expense_account = accounts['expense'] or move.journal_id.default_account_id
    #             if not debit_interim_account or not credit_expense_account:
    #                 continue
    #
    #             # Compute accounting fields.
    #             sign = -1 if move.move_type == 'out_refund' else 1
    #             price_unit = line._stock_account_get_anglo_saxon_price_unit()
    #             amount_currency = sign * line.quantity * price_unit
    #
    #             logger.warning(f"[ {line.name} ] ACCOUNT MOVE CREATING COGS [ {sign} * {line.quantity}  * {price_unit}  = {amount_currency}]")
    #
    #             if move.currency_id.is_zero(amount_currency) or float_is_zero(price_unit, precision_digits=price_unit_prec):
    #                 continue
    #
    #             # Add interim account line.
    #             lines_vals_list.append({
    #                 'name': line.name[:64],
    #                 'move_id': move.id,
    #                 'partner_id': move.commercial_partner_id.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'quantity': line.quantity,
    #                 'price_unit': price_unit,
    #                 'amount_currency': -amount_currency,
    #                 'account_id': debit_interim_account.id,
    #                 'display_type': 'cogs',
    #                 'tax_ids': [],
    #                 'cogs_origin_id': line.id,
    #             })
    #
    #             # Add expense account line.
    #             lines_vals_list.append({
    #                 'name': line.name[:64],
    #                 'move_id': move.id,
    #                 'partner_id': move.commercial_partner_id.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'quantity': line.quantity,
    #                 'price_unit': -price_unit,
    #                 'amount_currency': amount_currency,
    #                 'account_id': credit_expense_account.id,
    #                 'analytic_distribution': line.analytic_distribution,
    #                 'display_type': 'cogs',
    #                 'tax_ids': [],
    #                 'cogs_origin_id': line.id,
    #             })
    #
    #     return lines_vals_list
    #
