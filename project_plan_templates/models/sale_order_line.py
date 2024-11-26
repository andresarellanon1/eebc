from odoo import fields, models, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', compute="_products_project_domain", store=True)

    def _products_project_domain(self, is_project):
        for record in self:
            if is_project:
                record.products_project_domain = self.search['product.template'].search([
                    ('detailed_type', '=', 'service'),
                    ('sale_ok', '=', True),
                ])
            else:
                record.products_project_domain = self.search['product.template'].search([
                    ('sale_ok', '=', True),
                ])

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