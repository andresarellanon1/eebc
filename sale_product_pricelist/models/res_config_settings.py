# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    selected_product_pricelist_id = fields.Many2one('product.pricelist', string="Selected Product Pricelist")


class sale_configuration_settings(models.TransientModel):
    _inherit = "res.config.settings"

    selected_product_pricelist_id = fields.Many2one('product.pricelist',
                                                    string="Selected Product Pricelist",
                                                    related="company_id.selected_product_pricelist_id",
                                                    readonly=False)
