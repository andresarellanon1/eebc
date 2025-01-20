import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    branch_id = fields.Many2one('res.partner', string="Sucursal", readonly=True, compute="_compute_branch_id")

    def _compute_branch_id(self):
        self.branch_id = 0
