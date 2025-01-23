from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))

    @api.model
    def cancelar_cotizaciones_vencidas(self):
        quotations = self.search([('state', 'in', ['draft', 'sent'])])
        for order in quotations:
            order.action_cancel()

    @api.depends('partner_id')
    def _compute_user_id(self):
        for order in self:
            # Asigna siempre al usuario logueado como el user_id
            order.user_id = self.env.user
