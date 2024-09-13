from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.order_id.partner_id:
            products = self.env['product.supplierinfo'].search([('id', '=', self.partner_id.id)]).mapped('product_tmpl_id')
            
            logger.warning(f'1 {products}')
            product_ids = self.env['product.product'].search([('product_tmpl_id', 'in', products.ids)]).ids
            
            logger.warning(f'2 {product_ids}')
            
            self.order_line.product_ids = [(6, 0, product_ids)]
            logger.warning(f'Productos {self.product_ids}')