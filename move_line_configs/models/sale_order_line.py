from odoo import fields, models, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    complete_description = fields.Char(string='Large description', default=lambda self: self.name)

