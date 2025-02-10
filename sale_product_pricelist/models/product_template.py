from odoo import api, fields, models
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pricelist_line_ids = fields.Many2many(
        'product.pricelist.line',
        compute="_compute_product_pricelist_line_ids",
        store=True,
        string='Lineas de lista de precios')

    def _get_include_template_pricelist_ids(self):
        for product_template in self:
            company_id = product_template.company_id or self.env.company
            # Agregate all applicable pricelist for the given product template:
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('product_tmpl_id', '=', product_template.id), ('company_id', '=', company_id.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('categ_id', '=', product_template.categ_id.id), ('company_id', '=', company_id.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global'), ('company_id', '=', company_id.id)])
            pricelists_ids = set()
            for pricelist_id in items_direct_relation.pricelist_id:
                pricelists_ids.add(pricelist_id)
            for pricelist_id in items_category_relation.pricelist_id:
                pricelists_ids.add(pricelist_id)
            for pricelist_id in items_all_stock.pricelist_id:
                pricelists_ids.add(pricelist_id)
            return list(pricelists_ids)

        


    @api.depends_context('company')
    @api.depends("categ_id", "list_price", "standard_price")
    def _compute_product_pricelist_line_ids(self):
        logger.warning('Inicio _compute_product_pricelist_line_ids')

        # 1. Obtener y eliminar todas las líneas de precios en una sola operación
        all_pricelist_lines = self.mapped("product_pricelist_line_ids")
        if all_pricelist_lines:
            all_pricelist_lines.unlink()
        logger.warning('Se eliminaron todas las listas de precios')

        # 2. Preparar un diccionario para almacenar las líneas de precios por producto
        pricelist_lines_by_product = defaultdict(list)

        for product_template in self:
            applied_pricelists = product_template._get_include_template_pricelist_ids()

            for pricelist in applied_pricelists:
                pricelist_lines_by_product[product_template.id].append({
                    'name': pricelist.name,
                    'pricelist_id': pricelist.id,
                    'uom_id': product_template.uom_id.id,
                    'product_templ_id': product_template.id,
                    'currency_id': pricelist.currency_id.id,
                    'company_id': pricelist.company_id.id,
                    'is_special': pricelist.is_special
                })

        # 3. Escribir todas las nuevas líneas en una sola operación
        for product_template in self:
            product_template.sudo().write({
                'product_pricelist_line_ids': [(0, 0, vals) for vals in pricelist_lines_by_product.get(product_template.id, [])]
            })

        # 4. Recalcular los orphans en bloque
        self.mapped("product_pricelist_line_ids")._compute_is_orphan()

        logger.warning('Termino _compute_product_pricelist_line_ids')



    # @api.depends_context('company')
    # @api.depends("categ_id", "list_price", "standard_price")
    # def _compute_product_pricelist_line_ids(self):
    #     logger.warning('Inicio _compute_product_pricelist_line_ids')
    #     """
    #         Re-computes the price unit for all the 'product.pricelist.line' linked to this 'product.template'.
    #         Search for pricelist items applied on:
    #             - this product template id
    #             - this product template related category id
    #             - globally applied items
    #         and aggregates them.
    #         Get the price for each pricelist and create/update the lines for the template.
    #         Finally, re-computes the related o2m field for this 'product.template'.
    #     """
    #     # Obtener todas las líneas de precios en un solo paso y eliminarlas
    #     all_pricelist_lines = self.mapped("product_pricelist_line_ids")
    #     if all_pricelist_lines:
    #         all_pricelist_lines.unlink()
    #     logger.warning('Se eliminaron todas las listas de precios')


    #     for product_template in self:
    #         pricelist_line_vals = []
    #         applied_pricelists = product_template._get_include_template_pricelist_ids()
    #         # 1. Prepare vals for new lines
    #         for pricelist in applied_pricelists:
    #             pricelist_line_vals.append({
    #                 'name': pricelist.name,
    #                 'pricelist_id': pricelist.id,
    #                 'uom_id': product_template.uom_id.id,
    #                 'product_templ_id': product_template.id,
    #                 'currency_id': pricelist.currency_id.id,
    #                 'company_id': pricelist.company_id.id,
    #                 'is_special': pricelist.is_special
    #             })

    #         # 2. Unlink and delete all
    #         # product_template.sudo().write({'product_pricelist_line_ids': [(5, 0, 0)]})
    #         # 3. Link and create all
    #         # self.env.cr.commit()
    #         product_template.sudo().write({'product_pricelist_line_ids': [(0, 0, vals) for vals in pricelist_line_vals]})
    #         # 4. recompute orphans
    #         product_template.product_pricelist_line_ids._compute_is_orphan()
    #         # If nothing to link, write to `False`
    #         if len(pricelist_line_vals) <= 0:
    #             product_template.sudo().write({'product_pricelist_line_ids': False})

    #     logger.warning('Termino _compute_product_pricelist_line_ids')

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