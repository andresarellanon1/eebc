from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', store=True)

    def _products_project_domain(self, is_project):
        _logger.warning('ENTRÓ A LA FUNCIÓN')
        for record in self:
            if is_project:
                _logger.warning('IS PROJECT ES TRUE')

                products = self.env['product.template'].search([
                    ('detailed_type', '=', 'service'),
                    ('sale_ok', '=', True),
                ])
                record.products_project_domain = [(6, 0, products.ids)]
            else:
                _logger.warning('IS PROJECT ES FALSE')
                products = self.env['product.template'].search([
                    ('sale_ok', '=', True),
                ])
                record.products_project_domain = [(6, 0, products.ids)]


            _logger.warning(f'{record.products_project_domain.ids}')

    # product_template_id = fields.Many2one(
    #     string="Product Template",
    #     comodel_name='product.template',
    #     compute='_compute_product_template_id',
    #     readonly=False,
    #     search='_search_product_template_id',
    # #     # previously related='product_id.product_tmpl_id'
    # #     # not anymore since the field must be considered editable for product configurator logic
    # #     # without modifying the related product_id when updated.
    #     domain=[('sale_ok', '=', True)])

    # @api.depends('product_id')
    # def _compute_product_template_id(self):
    #     for line in self:
    #         line.product_template_id = line.product_id.product_tmpl_id