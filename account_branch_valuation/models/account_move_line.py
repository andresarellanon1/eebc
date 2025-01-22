import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move.line"

    sale_unit_cost = fields.Float('Costo Unitario', compute="_compute_sale_unit_cost", store=True, copy=True)

    @api.depends('sale_line_ids', 'sale_line_ids.purchase_price')
    def _compute_sale_unit_cost(self):
        """
            Cost used when generating custom reports, calculated from the sale document and it's dynamically re-computed whenever the sale line is updated,
            when the report is being generated, this value will have the most recent value based on the stock valuation layers of the OUT picking.
            By default it have a value and the reports may change from one day to another based on the validated pickings in those days cuz the value will recompute.
        """
        for line in self:
            sum_cost = 0.00
            for sale_line in line.sale_line_ids:
                sum_cost += sale_line.purchase_price
            if len(line.sale_line_ids) <= 0:
                line.sale_unit_cost = 0.00
            else:
                line.sale_unit_cost = sum_cost / len(line.sale_line_ids)

    # def _stock_account_get_anglo_saxon_price_unit(self):
    #     """
    #         Overwritten
    #         The returned value of this method is used as the amount for the accounting expenses (COGS) for this invoice.
    #         We use the field `sale_unit_cost` computed from the sale.order.line `purchase_price`,
    #         which is computed using the stock layers available for the current branch.
    #
    #         If no sale order is provied via the origin fields then we default to the custom field `accounting_standard_price`
    #         instead of base field 'standard_price'.
    #         Check docstring on the compute method of this field for more details on it's behavior and what value does it represent.
    #         (TLDR: it's the overall company avg cost computed directly from the values in the purchase documents)
    #         The algorithm behind the  `accounting_standard_price` field may be customized in the branches purchase module.
    #     """
    #     self.ensure_one()
    #     branch_average_price_unit = 0.0
    #     if not self.product_id:
    #         return self.price_unit  # this was probably manually typed into the price field on the invoice line
    #     original_line = next(
    #         (line for line in self.move_id.reversed_entry_id.line_ids
    #          if line.display_type == 'cogs' and line.product_id == self.product_id and line.product_uom_id == self.product_uom_id and line.price_unit >= 0),
    #         None)
    #     if original_line:
    #         branch_average_price_unit = original_line.price_unit
    #     else:
    #         so_line = self.sale_line_ids and self.sale_line_ids[-1] or False
    #         if so_line:
    #             is_line_reversing = self.move_id.move_type == 'out_refund'
    #             qty_to_invoice = self.product_uom_id._compute_quantity(self.quantity, self.product_id.uom_id)
    #             account_moves = so_line.invoice_lines.move_id.filtered(lambda m: m.state == 'posted' and bool(m.reversed_entry_id) == is_line_reversing)
    #
    #             posted_cogs = account_moves.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
    #             qty_invoiced = sum([line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id) for line in posted_cogs])
    #             value_invoiced = sum(posted_cogs.mapped('balance'))
    #
    #             reversal_cogs = posted_cogs.move_id.reversal_move_id.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
    #             qty_invoiced -= sum([line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id) for line in reversal_cogs])
    #             value_invoiced -= sum(reversal_cogs.mapped('balance'))
    #
    #             product = self.product_id.with_company(self.company_id).with_context(value_invoiced=value_invoiced)
    #             # average_price_unit =
    #             branch_average_price_unit = self.sale_unit_cost if len(self.sale_line_ids) <= 0 else product._compute_average_price(qty_invoiced, qty_to_invoice, so_line.move_ids, is_returned=is_line_reversing)
    #             price_unit = self.product_id.uom_id.with_company(self.company_id)._compute_price(branch_average_price_unit, self.product_uom_id)
    #     return price_unit


# original
"""
def _stock_account_get_anglo_saxon_price_unit(self):
    self.ensure_one()
    if not self.product_id:
        return self.price_unit
    original_line = self.move_id.reversed_entry_id.line_ids.filtered(
        lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and
        l.product_uom_id == self.product_uom_id and l.price_unit >= 0)
    original_line = original_line and original_line[0]
    return original_line.price_unit if original_line \
        else self.product_id.with_company(self.company_id)._stock_account_get_anglo_saxon_price_unit(uom=self.product_uom_id)
"""
# product.product original
"""
    # -------------------------------------------------------------------------
    # Anglo saxon helpers
    # -------------------------------------------------------------------------
    def _stock_account_get_anglo_saxon_price_unit(self, uom=False):
        price = self.standard_price
        if not self or not uom or self.uom_id.id == uom.id:
            return price or 0.0
        return self.uom_id._compute_price(price, uom)
"""

# sale_stock overwrite
"""
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _sale_can_be_reinvoice(self):
        self.ensure_one()
        return self.move_type != 'entry' and self.display_type != 'cogs' and super(AccountMoveLine, self)._sale_can_be_reinvoice()

    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()

        so_line = self.sale_line_ids and self.sale_line_ids[-1] or False
        if so_line:
            is_line_reversing = self.move_id.move_type == 'out_refund'
            qty_to_invoice = self.product_uom_id._compute_quantity(self.quantity, self.product_id.uom_id)
            account_moves = so_line.invoice_lines.move_id.filtered(lambda m: m.state == 'posted' and bool(m.reversed_entry_id) == is_line_reversing)

            posted_cogs = account_moves.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
            qty_invoiced = sum([line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id) for line in posted_cogs])
            value_invoiced = sum(posted_cogs.mapped('balance'))

            reversal_cogs = posted_cogs.move_id.reversal_move_id.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
            qty_invoiced -= sum([line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id) for line in reversal_cogs])
            value_invoiced -= sum(reversal_cogs.mapped('balance'))

            product = self.product_id.with_company(self.company_id).with_context(value_invoiced=value_invoiced)
            average_price_unit = product._compute_average_price(qty_invoiced, qty_to_invoice, so_line.move_ids, is_returned=is_line_reversing)
            price_unit = self.product_id.uom_id.with_company(self.company_id)._compute_price(average_price_unit, self.product_uom_id)
        return price_unit

"""
