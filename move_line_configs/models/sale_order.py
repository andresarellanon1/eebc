from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    complete_description = fields.Char(string='Large description', default=lambda self: self.name)

    use_large_description = fields.Boolean(string="Usar descripcion")