from odoo import api, fields, models
from datetime import date
import logging
logger = logging.getLogger(__name__)


class ProductPricelistLine(models.Model):
    _inherit = 'product.pricelist.line'
