from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            products = self.env['product.supplierinfo'].search([('partner_id', '=', self.partner_id.id)]).mapped('product_tmpl_id')
            
            logger.warning(f'1 {products.ids}')
            self.order_line.product_template_id = [(6, 0, products)]