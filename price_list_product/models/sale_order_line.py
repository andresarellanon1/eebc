from odoo import models, api, fields
import logging

logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_pricelist_id = fields.Many2one("product.pricelist.line",
                                           string="Lista precio")
    pricelist_unit_price = fields.Float('Precio de lista de precio', digits="Product Price", compute="_compute_pl_unit_price", store=True)
    branch_id = fields.Many2one('res.partner', string='Sucursal', related="order_id.branch_id")
    # branch_id = fields.Many2one('res.partner', string='Sucursal', domain="[('is_branch','=',True)]")

    @api.depends('product_pricelist_id')
    def _compute_pl_unit_price(self):
        for line in self:
            line.pricelist_unit_price = line.product_pricelist_id.unit_price

    @api.onchange("product_pricelist_id")
    def product_pricelist_id_change(self):
        for line in self:
            line.price_unit = line.product_pricelist_id.unit_price
