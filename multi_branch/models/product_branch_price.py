from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProductBranchPrice(models.Model):

    _name = 'product.branch.price'
    _description = 'Price by branch'

    branch_id = fields.Many2one('res.branch', string='Branch', required=True)
    product_id = fields.Many2one('product.template', string='Product', required=True)
    branch_price = fields.Float(string='Branch Price', required=True)

    @api.constrains('branch_id', 'product_id')
    def _check_unique_branch_product(self):
        for record in self:
            duplicate = self.search([
                ('branch_id', '=', record.branch_id.id),
                ('product_id', '=', record.product_id.id),
                ('id', '!=', record.id)
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    'Each product must have a unique price per branch! (Branch: %s, Product: %s)' % 
                    (record.branch_id.name, record.product_id.name)
                )