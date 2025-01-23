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
    allow_price_recompute = fields.Boolean(default=True,
                                           string="Permitir precio dinámico?",
                                           help="Al activar esta casilla tendra las siguientes consecuencias:\n"
                                           "Al comprar con este proveedor, el precio de esta linea se actualizara.\n"
                                           "Los cambios en el campo de ultimo precio van a re-computar el precio del vendedor asignandole el mismo precio.\n"
                                           "Si este proveedor es el princiapl o el mas reciente sin principal;\n "
                                           "El campo de costo del producto se actualizara, usando la ultima divisa usada por el proveedor en caso"
                                           "de requerir cambio de divisas.")
    lead_time = fields.Integer(string='Lead Time',
                               help='Tiempo de entrega configurado en el contacto. Solo se computa desde el contacto la primera vez que se registra la linea de proveedor. Puede cambiarlo libremente sin afectar el campo original del contacto.',
                               compute="_compute_lead_time",
                               store=True)

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

    @api.model_create_multi
    def create(self, vals_list):
        suppliers_info = super(ProductSupplierInfo, self).create(vals_list)

        for supplier_info in suppliers_info:
            supplier_info._check_coherence()
            supplier_info._compute_delay()

        return suppliers_info

    def write(self, vals):
        res = super(ProductSupplierInfo, self).write(vals)
        self._check_coherence()
        return res

    @api.constrains('min_qty', 'multiplier')
    def _check_coherence(self):
        for record in self:
            if record.min_qty and record.multiplier and record.min_qty % record.multiplier != 0:
                raise ValidationError("Cantidad mínima debe ser divisible por el múltiplo.")
            if record.multiplier and record.min_qty and record.min_qty % record.multiplier != 0:
                raise ValidationError("Cantidad mínima debe ser divisible por el múltiplo.")
