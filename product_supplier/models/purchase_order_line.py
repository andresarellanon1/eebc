from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_ids = fields.Many2many('product.product')

    @api.onchange('order_id.partner_id')
    def _onchange_partner_id(self):
        if self.order_id.partner_id:
            products = self.env['product.supplierinfo'].search([('name', '=', self.order_id.partner_id.id)]).mapped('product_tmpl_id')
            
            product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', products.ids)]).ids
            
            self.product_ids = [(6, 0, product_ids)]