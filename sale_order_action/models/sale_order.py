from odoo import api, models, fields

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def cancelar_cotizaciones_vencidas(self):
        quotations = self.search([('state', 'in', ['draft', 'sent'])])
        for order in quotations:
            order.action_cancel()