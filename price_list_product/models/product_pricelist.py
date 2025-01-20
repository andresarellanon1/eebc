import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    branch_id = fields.Many2one('res.partner', string='Sucursal', domain="[('is_branch','=',True)]")

    @api.depends('item_ids')
    def _compute_filtered_item_ids(self):
        for rec in self:
            rec.filtered_item_ids = False
            origin_res_model = rec.env.context.get('origin_res_model', False)
            origin_res_id = rec.env.context.get('origin_res_id', False)
            pricelist_id = rec.env.context.get('pricelist_id', False)

            if not origin_res_model or not origin_res_id or not pricelist_id:
                return

            if origin_res_model == 'product.template':
                rec.filtered_item_ids = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist_id),
                    ('product_tmpl_id', '=', origin_res_id),
                    ('applied_on', '=', '1_product')
                ])

            elif origin_res_model == 'product.product':
                rec.filtered_item_ids = self.env['product.pricelist.item'].search([
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
