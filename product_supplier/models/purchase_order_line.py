from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('order_id.partner_id')
    def _onchange_partner_id(self):
        if self.order_id.partner_id:
            supplier_info = self.env['product.supplierinfo'].search([('name', '=', self.order_id.partner_id.id)])
            product_templates = supplier_info.mapped('product_tmpl_id')
            product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', product_templates)]).ids
            
            return {
                'domain': {
                    'product_id': [('id', 'in', product_ids)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': []
                }
            }