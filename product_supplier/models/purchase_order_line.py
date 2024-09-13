from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('order_id.partner_id')
    def _onchange_partner_id(self):
        if self.order_id.partner_id:
            product_templates = self.env['product.template'].search([('partner_id', '=', self.order_id.partner_id.id)])
            
            product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', product_templates.ids)]).ids
            
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