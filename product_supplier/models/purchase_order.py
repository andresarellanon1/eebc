from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            supplier_products = self.env['product.supplierinfo'].search([('partner_id', '=', self.partner_id.id)]).mapped('product_tmpl_id')
            logger.warning(f'1 {supplier_products.ids}')
            self.order_line.supplier_products_ids = [(6, 0, supplier_products.ids)]
            logger.warning(f'Supplier products for partner {self.partner_id.id}: {supplier_products.ids}')
        else:
            self.order_line.supplier_products_ids = [(5, 0, 0)]