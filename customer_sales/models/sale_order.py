from odoo import _, api, fields, models
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    material_change = fields.Boolean(default=False, string="Cambio de material")
    customer_reference = fields.Char(string="Orden de compra", help="Referencia de la orden de compra del cliente. Este campo no representa una orden de compra dentro de odoo. Se refiere a una orden de compra en el sistema del cliente.")
    urgency_type = fields.Selection(
        [
            ("order", "Retraso en el pedido"),
            ("goods", "Retraso en la mercancía"),
            ("customer", "Cliente"),
        ],
        string="Tipo de urgencia"
    )

    quotation_user_id = fields.Many2one(
        comodel_name='res.users',
        string="Elaborado por")
    
    contrat_id = fields.Many2one(
        'limit.contrat',
        string="Contrato")

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['material_change'] = self.material_change
        return res

    def _compute_quotation_user(self):
        for order in self:
            order.quotation_user_id = self.env.user

    @api.onchange("partner_id")
    def onchange_partner_invoicing(self):
        for order in self:
            order.partner_invoice_id = order.partner_id
            order.partner_shipping_id = order.partner_id
