from odoo import models, api, fields, _
import logging
logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    dummy_field = fields.Integer(compute="_compute_dummy_field", store=False)
    branch_id = fields.Many2one('res.partner', string='Sucursal', domain="[('is_branch','=',True)]")

    def _compute_dummy_field(self):
        for sol in self.order_line:
            if sol.product_id and sol.product_uom:
                sol.product_template_id.get_product_pricelist()

        self.dummy_field = 0
