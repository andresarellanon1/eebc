from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    last_price = fields.Float(string='Último precio',
                              digits="Product Price",
                              help="Se computa desde la última orden de compra relacionada al contacto y al producto. Cuando este valor se computa también se computa el precio.",
                              readonly=True)
    multiplier = fields.Integer(string='Múltiplo',
                                help="Múltiplo de compra. Las cantidades compradas y la cantidad mínima deben ser múltiplos del valor indicado en este campo.",
                                default="1")
    is_main_supplier = fields.Boolean(default=False, string="Principal")
    allow_price_recompute = fields.Boolean(default=True, string="Precio dinámico")
    lead_time = fields.Integer(string='Lead Time',
                               help='Tiempo de entrega configurado en el contacto',
                               compute="_compute_lead_time",
                               store=True,
                               readonly=True)

    @api.onchange('last_price')
    def _compute_price_eq_last_price(self):
        for seller in self:
            seller.price = seller.last_price

    @api.depends('partner_id', 'partner_id.lead_time')
    def _compute_lead_time(self):
        for seller in self:
            if seller.partner_id.lead_time:
                seller.lead_time = seller.partner_id.lead_time

    @api.onchange('lead_time')
    def _compute_delay(self):
        for seller in self:
            seller.delay = seller.partner_id.lead_time

    @api.depends('lead_time')
    def depends_delay_lead_time(self):
        self._compute_delay()

    @api.constrains('is_main_supplier', 'product_tmpl_id')
    def _check_main_supplier_constraint(self):
        for record in self:
            if record.is_main_supplier:
                main_supplier_count = self.search_count([
                    ('product_tmpl_id', '=', record.product_tmpl_id.id),
                    ('is_main_supplier', '=', True),
                    ('id', '!=', record.id),
                ])
                if main_supplier_count > 0:
                    raise ValidationError(
                        "Solo un proveedor principal por producto")
