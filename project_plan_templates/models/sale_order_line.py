from odoo import fields, models, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', compute="_products_project_domain", store=True)

    # @api.depends()
    # def _products_project_domain(self):
    #     for record in self:
            

    # @api.depends()
    # def _compute_partner_domain_ids(self):
    #     for record in self:
    #         partner_ids = record.move_ids.mapped('partner_id.id')
    #         child_ids = record.move_ids.mapped('partner_id.child_ids.id')
    #         company_partner_id = record.company_id.partner_id.id if record.company_id and record.company_id.partner_id else False

    #         all_partner_ids = partner_ids + child_ids
    #         if company_partner_id:
    #             all_partner_ids.append(company_partner_id)

    #         record.partner_domain_ids = self.env['res.partner'].browse(all_partner_ids)


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