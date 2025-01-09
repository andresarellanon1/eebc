from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', store=True, compute="_products_project_domain")
    code = fields.Char(string="Code")

    @api.depends('order_id', 'order_id.is_project')
    def _products_project_domain(self):
        for record in self:
            if record.order_id.is_project:

                products = self.env['product.template'].search([
                    ('detailed_type', '=', 'service'),
                    ('project_plan_id', '!=', False),
                    ('sale_ok', '=', True),
                ])

                record.products_project_domain = [(6, 0, products.ids)]
            else:

                products = self.env['product.template'].search([
                    ('sale_ok', '=', True),
                    ('detailed_type', '!=', 'service'),
                ])

                record.products_project_domain = [(6, 0, products.ids)]

    is_long_name = fields.Boolean(string="Nombre Largo", compute="_compute_is_long_name")

    def _compute_is_long_name(self):
        for line in self:
            line.is_long_name = line.name and len(line.name) > 9
