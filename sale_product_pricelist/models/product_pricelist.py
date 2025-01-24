import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def write(self, vals):
        res = super(ProductPricelist, self).write(vals)
        for line in self:
            line._compute_product_pricelist_lines()
        return res

    def _compute_product_pricelist_lines(self):
        for pricelist in self:
            items_direct_relation_variant = self.env['product.pricelist.item'].search([('applied_on', '=', '0_product_variant'), ('pricelist_id', '=', pricelist.id)])
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('pricelist_id', '=', pricelist.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('pricelist_id', '=', pricelist.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global')])

            if items_direct_relation.product_tmpl_id:
                product_template = self.env["product.template"].search([('id', '=', items_direct_relation.product_tmpl_id.id)])
                product_template._compute_product_pricelist_line_ids()

            if items_direct_relation_variant.product_id:
                product = self.env["product.product"].search([('id', '=', items_direct_relation.product_id.id)])
                product.product_tmplt_id._compute_product_pricelist_line_ids()

            if items_category_relation.categ_id:
                product_templates = self.env["product.template"].search([('categ_id', '=', items_category_relation.categ_id.id)])
                product_templates._compute_product_pricelist_line_ids()

            if len(items_all_stock) > 0:
                self.env["product.template"]._compute_product_pricelist_line_ids()

    @api.depends('item_ids')
    def _compute_filtered_item_ids(self):
        for pricelist in self:
            pricelist.filtered_item_ids = False
            origin_res_model = pricelist.env.context.get('origin_res_model', False)
            origin_res_id = pricelist.env.context.get('origin_res_id', False)
            pricelist_id = pricelist.env.context.get('pricelist_id', False)

            if not origin_res_model or not origin_res_id or not pricelist_id:
                return

            if origin_res_model == 'product.template':
                pricelist.filtered_item_ids = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist_id),
                    ('product_tmpl_id', '=', origin_res_id),
                    ('applied_on', '=', '1_product')
                ])

            elif origin_res_model == 'product.product':
                pricelist.filtered_item_ids = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist_id),
                    ('product_id', '=', origin_res_id),
                    ('applied_on', '=', '0_product_variant')
                ])

    def inverse_filtered_item_ids(self):
        self.item_ids = self.filtered_item_ids | self.item_ids

    filtered_item_ids = fields.One2many(
        comodel_name='product.pricelist.item',
        inverse_name='pricelist_id',
        string="Pricelist Rules",
        domain=[
            '&',
            '|', ('product_tmpl_id', '=', None), ('product_tmpl_id.active', '=', True),
            '|', ('product_id', '=', None), ('product_id.active', '=', True),
        ],
        copy=True, compute="_compute_filtered_item_ids", inverse='inverse_filtered_item_ids')
