from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)



class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def cancelar_cotizaciones_vencidas(self):
        quotations = self.search([('state', 'in', ['draft', 'sent'])])
        for order in quotations:
            order.action_cancel()

    @api.one
    @api.depends('partner_id')
    def _compute_user_id(self):
        _logger.warning('Es nuestro compute')
        for order in self:
            # Aquí puedes cambiar la lógica a tu gusto
            if order.partner_id and not (order._origin.id and order.user_id):
                order.user_id = order.partner_id.user_id or self.env.user  # Ejemplo de nueva lógica