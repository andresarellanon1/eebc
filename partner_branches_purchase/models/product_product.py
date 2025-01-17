
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_repr, float_round, float_compare
from odoo.exceptions import ValidationError
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # def _stock_account_get_anglo_saxon_price_unit(self, uom=False):
    #     price = self.standard_price
    #     logger.warning(f"=== Product Product anglosaxon helper - PRICE: {price} ===")
    #     if not self or not uom or self.uom_id.id == uom.id:
    #         return price or 0.0
    #     return self.uom_id._compute_price(price, uom)
