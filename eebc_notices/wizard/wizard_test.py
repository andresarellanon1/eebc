from odoo import models, fields

class ProductSelectionWizard(models.TransientModel):
    _name = 'product.selection.wizard'
    _description = 'Wizard for Product Selection'

    product_ids = fields.Many2many(
        'product.product',
        string='Products',
    )
    quantity_ids = fields.One2many(
        'product.selection.line',
        'wizard_id',
        string='Quantities',
    )

class ProductSelectionLine(models.TransientModel):
    _name = 'product.selection.line'
    _description = 'Product Selection Line'

    wizard_id = fields.Many2one(
        'product.selection.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
    )
