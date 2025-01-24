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

    def _get_include_template_pricelist_ids(self):
        for product_template in self:
            company_id = product_template.company_id or self.env.company
            logger.warning(f"found company_id  {company_id.name}")
            # Agregate all applicable pricelist for the given product template:
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('product_tmpl_id', '=', product_template.id), ('company_id', '=', company_id.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('categ_id', '=', product_template.categ_id.id), ('company_id', '=', company_id.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global'), ('company_id', '=', company_id.id)])
            pricelists_ids = []
            for pricelist_id in items_direct_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            for pricelist_id in items_category_relation.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            for pricelist_id in items_all_stock.pricelist_id:
                pricelists_ids.append(pricelist_id.id)
            logger.warning(f"found pricelists {pricelists_ids}")
            if pricelists_ids:
                product_template.sudo().write({'include_template_pricelist_ids': [(6, 0, pricelists_ids)]})
            else:
                product_template.sudo().write({'include_template_pricelist_ids': [(6, 0, 0)]})

    @api.depends_context('company')
    @api.depends("list_price", "standard_price")
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
            pricelists = product_template._get_include_template_pricelist_ids()
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
            # NOTE: Comand `0`: Unlink-all and Link-all
            product_template.sudo().write({'product_pricelist_line_ids': [(6, 0, product_pricelist)]})

    def get_min_sale_price(self, currency_id):
        """
            Helper to use in validations.
            Returns the lowest price out of all pricelist lines.
        """
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        for product_template in self:
            lowest_value = 0.0000
            for pricelist in product_template.product_pricelist_line_ids:
                if (lowest_value == 0.00 or pricelist.unit_price < lowest_value) and (pricelist.currency_id.id == currency_id.id):
                    lowest_value = pricelist.unit_price
            lowest_value = round(lowest_value, price_unit_prec)
            return lowest_value
