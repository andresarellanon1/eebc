from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging
logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pricelist_line_ids = fields.One2many(
        'product.pricelist.line',
        'product_templ_id',
        compute="_compute_product_pricelist_line_ids",
        store=True,
        string='Lineas de lista de precios')

    include_template_pricelist_ids = fields.Many2many(
        'product.pricelist',
        compute="_compute_include_template_pricelist_ids",
        store=True,
        string='Aparece en listas de precios')

    @api.depends_context('company')
    @api.depends("company_id", "pricelist_item_count")
    def _compute_include_template_pricelist_ids(self):
        for product_template in self:
            # Agregate all applicable pricelist for the given product template:
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('product_tmpl_id', '=', product_template.id), ('company_id', '=', self.env.company.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('categ_id', '=', product_template.categ_id.id), ('company_id', '=', self.env.company.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global'), ('company_id', '=', self.env.company.id)])
            pricelists_ids = []
            for pricelist_id in items_direct_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            for pricelist_id in items_category_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            for pricelist_id in items_all_stock.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            logger.warning(f"Found pricelists {pricelists_ids} for product {product_template}")
            product_template.include_template_pricelist_ids = [(6, 0, pricelists_ids)]

    @api.depends_context('company')
    @api.depends("company_id", "list_price", "standard_price", "include_template_pricelist_ids")
    def _compute_product_pricelist_line_ids(self):
        """
            Re-computes the price unit for all the 'product.pricelist.line' linked to this 'product.template'.
            Search for pricelist items applied on:
                - this product template id
                - this product template related category id
                - globally applied items
            and aggregates them.
            Get the price for each pricelist and create/update the lines for the template.
            Finally, re-computes the related o2m field for this 'product.template'.
        """
        for product_template in self:
            product_pricelist = []
            pricelists = product_template.include_template_pricelist_ids
            dict_product_pricelist_id = {}
            if not pricelists:
                return
            for pricelist in pricelists:
                if pricelist.id in dict_product_pricelist_id:
                    dict_product_pricelist_id[pricelist.id].write({
                        'name': pricelist.name,
                        'uom_id': product_template.uom_id.id,
                        'currency_id': pricelist.currency_id.id,
                        'is_special': pricelist.is_special
                    })
                else:
                    product_pricelist.append(self.env['product.pricelist.line'].create({
                        'name': pricelist.name,
                        'pricelist_id': pricelist.id,
                        'uom_id': product_template.uom_id.id,
                        'product_templ_id': product_template.id,
                        'currency_id': pricelist.currency_id.id,
                        'is_special': pricelist.is_special
                    }).id)
            product_template.product_pricelist_line_ids = [(6, 0, product_pricelist)]

    def get_min_sale_price(self, currency_id):
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        for product_template in self:
            lowest_value = 0.0000
            for pricelist in product_template.product_pricelist_line_ids:
                if (lowest_value == 0.00 or pricelist.unit_price < lowest_value) and (pricelist.currency_id.id == currency_id.id):
                    lowest_value = pricelist.unit_price
            lowest_value = round(lowest_value, price_unit_prec)
            return lowest_value
