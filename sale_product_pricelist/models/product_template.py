from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging
logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pricelist_id = fields.One2many(
        'product.pricelist.line', 'product_templ_id', 'Lista de precios')

    def _compute_dummy_field(self):
        for rec in self:
            rec.get_product_pricelist()
            rec.dummy_field = 0

    dummy_field = fields.Integer(compute=_compute_dummy_field, store=False)

    def compute_valid_price_lists(self):
        for product_template in self:
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('product_tmpl_id', '=', product_template.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('categ_id', '=', product_template.categ_id.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global')])

            pricelists_ids = []
            for pricelist_id in items_direct_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)

            for pricelist_id in items_category_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)

            for pricelist_id in items_all_stock.pricelist_id:
                pricelists_ids.append(pricelist_id.id)

            pricelists = self.env['product.pricelist'].search([('id', 'in', pricelists_ids)])

            return pricelists

    def get_product_pricelist(self):
        for product_template in self:
            product_pricelist = []
            pricelists = product_template.compute_valid_price_lists()
            dict_product_pricelist_id = {}

            for pr_pricelist in product_template.product_pricelist_id:
                dict_product_pricelist_id[pr_pricelist.pricelist_id.id] = pr_pricelist

            if pricelists:
                for pricelist in pricelists:
                    if pricelist.id in dict_product_pricelist_id:
                        pricelist_line = dict_product_pricelist_id[pricelist.id]
                        pricelist_line.write({
                            'name': pricelist.name,
                            'uom_id': product_template.uom_id.id,
                            'currency_id': pricelist.currency_id.id,
                            'is_special': pricelist.is_special
                        })
                    else:
                        pricelist_line = self.env['product.pricelist.line'].create({
                            'name': pricelist.name,
                            'pricelist_id': pricelist.id,
                            'uom_id': product_template.uom_id.id,
                            'product_templ_id': product_template.id,
                            'currency_id': pricelist.currency_id.id,
                            'is_special': pricelist.is_special
                        })

                    product_pricelist.append(pricelist_line.id)

                product_template.sudo().update(
                    {'product_pricelist_id': [(6, 0, product_pricelist)], })

    def get_min_sale_price(self, currency_id):

        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')

        for product_template in self:
            lowest_value = 0.0000
            for pricelist in product_template.product_pricelist_id:

                logger.warning(f"pricelist.unit_price: {pricelist.unit_price}")

                if (lowest_value == 0.00 or pricelist.unit_price < lowest_value) and (pricelist.currency_id.id == currency_id.id):
                    lowest_value = pricelist.unit_price

            lowest_value = round(lowest_value, price_unit_prec)

            return lowest_value
