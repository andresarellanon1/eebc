from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_products_ids = fields.Many2many('product.template', string='Supplier Products', compute='_compute_supplier_products', store=True)
    product_template_id = fields.Many2one('product.template')

    @api.depends('order_id.partner_id')
    def _compute_supplier_products(self):
        for line in self:
            partner = line.order_id.partner_id
            if partner:
                supplier_products = self.env['product.supplierinfo'].search([('partner_id', '=', partner.id)]).mapped('product_tmpl_id')
                line.supplier_products_ids = [(6, 0, supplier_products.ids)]
                logger.warning(f'Supplier products for partner {partner.id}: {supplier_products.ids}')
            else:
                line.supplier_products_ids = [(5, 0, 0)]
from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_products_ids = fields.Many2many('product.template', string='Supplier Products', compute='_compute_supplier_products', store=True)

    @api.depends('order_id.partner_id')
    def _compute_supplier_products(self):
        for line in self:
            partner = line.order_id.partner_id
            if partner:
                supplier_products = self.env['product.supplierinfo'].search([('partner_id', '=', partner.id)]).mapped('product_tmpl_id')
                line.supplier_products_ids = [(6, 0, supplier_products.ids)]
                logger.warning(f'Supplier products for partner {partner.id}: {supplier_products.ids}')
            else:
                line.supplier_products_ids = [(5, 0, 0)]