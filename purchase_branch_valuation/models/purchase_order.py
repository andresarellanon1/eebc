from datetime import date
from odoo import api, models, _
from odoo.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


# Computes the list price of the product after updating prices of the supplier.
# If allow price recompute is active, at this point the product list price will be updated to the latest currency-price_unit of the supplier.
# line.product_id.product_tmpl_id._compute_list_price()
# conversion_date = line.date_approve or date.today()
# if line.landed_cost:
#     conversion_date = line.landed_cost.date
# supplier.conversion_date = conversion_date
# line.product_id.product_tmpl_id._compute_standard_price()
# Compute the global averange price. Used for defaulting accounting costs.
# line.product_id.product_tmpl_id._compute_accounting_standard_price()
