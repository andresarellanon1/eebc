from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', store=True, compute="_products_project_domain")
    code = fields.Char(string="Code")

    @api.depends('order_id', 'order_id.is_project')
    def _products_project_domain(self):
        _logger.warning('ENTRÓ A LA FUNCIÓN')
        for record in self:

            _logger.warning('order_id: %s', record.order_id)
            _logger.warning('order_id: %s', record.order_id.is_project)

            
            if record.order_id.is_project:
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