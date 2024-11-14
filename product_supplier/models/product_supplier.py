from odoo import fields, models, api
from odoo.exceptions import ValidationError


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
    supplier_retention = fields.Float(string="Retencion Proveedor")

    @api.onchange('last_price')
    def _compute_price_eq_last_price(self):
        for seller in self:
            seller.price = seller.last_price

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

    @api.onchange('supplier_retention')
    def _check_retention(self):
        for record in self:
            retention = record.supplier_retention
            if retention < 0 or retention > 1:
                raise ValidationError(
                    "El valor de la retención debe estar dentro del rango entre el 0 y el 1."
                )
