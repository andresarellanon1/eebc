from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = "sale.order"

    use_large_description = fields.Boolean(string="Usar descripción larga", default=False)

    @api.onchange('use_large_description')
    def _onchange_description(self):
        order_line.use_large_description = self.use_large_description