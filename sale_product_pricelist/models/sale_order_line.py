from odoo import models, api, fields
import logging

logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_pricelist_id = fields.Many2one("product.pricelist.line", string="Lista precio")
    pricelist_unit_price = fields.Float('Precio de lista de precio', digits="Product Price", compute="_compute_pl_unit_price", store=True)

    @api.onchange("product_id")
    def _onchange_product_pricelist(self):
        """
            Always compute the new prices after selecting a product_id.
        """
        for line in self:
            line.product_template_id._compute_product_pricelist()

    @api.depends('product_pricelist_id')
    def _compute_pl_unit_price(self):
        """
            Set the exact price of the pricelist for this line.
            This can not be modified by the user.
        """
        for line in self:
            line.pricelist_unit_price = line.product_pricelist_id.unit_price

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.safe_margin')
    def _compute_price_unit(self):
        """
            Set the actual price of the line.
            This can be modified by the user.
        """
        super(SaleOrderLine, self)._compute_price_unit()
        for line in self:
            line.unit_price = line.product_pricelist_id.unit_price
