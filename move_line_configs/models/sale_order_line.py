from odoo import fields, models, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    complete_description = fields.Char(string='Large description', default=lambda self: self.name)
    use_large_description = fields.Boolean(string='Usar descripción larga')

    @api.onchange('order_id.use_large_description')
    def _onchange_description(self):
        use_large_description = order_id.use_large_description