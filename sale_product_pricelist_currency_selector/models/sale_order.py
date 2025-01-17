import logging
from odoo import models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"


def _compute_pricelist_prices(self):
    """
    Override to implement custom pricelist computing
    e.g.

    """
    for order in self:
        for line in order.order_line:
            line._compute_pricelist_price_unit()
