import logging
from odoo import models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_product_pricelist(self):
        """
            Override
            Implemented custom method to recompute price unit per line.
            Uses the pricelist lines of the product template to find the price unit with the most priority in the accurate currency and branch.
        """
        for order in self:
            for line in order.order_line:
                line._compute_pricelist_price_unit()
