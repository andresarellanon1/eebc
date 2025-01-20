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
            cost = 0.00

            if line.move_id.pre_invoice or line.move_id.is_government or line.move_id.material_change:
                line.sale_unit_cost = 0.00
                continue

            for sale_line in line.sale_line_ids:
                cost += sale_line.purchase_price

            if len(line.sale_line_ids) <= 0:
                line.sale_unit_cost = 0.00

            else:
                line.sale_unit_cost = cost / len(line.sale_line_ids)

    # COST USED FOR ACCOUNTING
    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()

        if not self.product_id:
            return self.price_unit  # this was probably manually typed into the price field on the invoice line

        original_line = next(
            (line for line in self.move_id.reversed_entry_id.line_ids
             if line.display_type == 'cogs' and line.product_id == self.product_id and line.product_uom_id == self.product_uom_id and line.price_unit >= 0),
            None)

        if original_line:
            return original_line.price_unit
        else:
            # We use custom field here instead of base field 'standard_price'. Check docstring on the compute method of this field for more detailds
            return self.product_id.sale_unit_cost
