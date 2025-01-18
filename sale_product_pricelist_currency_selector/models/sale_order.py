import logging
from odoo import models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_product_pricelist(self):
        """
        Override
        Implemented custom method to recompute price unit per line.
        Uses the pricelist_line of the product template selected or the corresponding to the default, priority or secondary pricelist selected on the customer.
        """
        for order in self:
            for line in order.order_line:
                line._compute_pricelist_price_unit()
