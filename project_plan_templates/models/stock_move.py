from odoo import fields, models, api

class StockMove(models.Model):

    _inherit = 'stock.move'

    product_id = fields.Many2one(
        'product.product', 'Product',
        check_company=True,
        domain="[('type', '=', 'consu')]", index=True, required=True)

    product_uom = fields.Many2one(
        'uom.uom', string="Unidad", domain="[('category_id', '=', product_uom_category_id)]")