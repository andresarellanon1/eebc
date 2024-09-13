from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('order_id.partner_id')
    def _onchange_partner_id(self):
        if self.order_id.partner_id:
            supplier_products = self.env['product.supplierinfo'].search([
                ('id', '=', self.order_id.partner_id.id)
            ]).mapped('product_tmpl_id')

            return {
                'domain': {
                    'product_id': [('product_tmpl_id', 'in', supplier_products)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': []
                }
            }