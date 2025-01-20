from odoo import api, fields, models
from datetime import date
import logging
logger = logging.getLogger(__name__)


class ProductPricelistLine(models.Model):
    _name = 'product.pricelist.line'
    _description = 'Linea de lista de precios para producto'

    name = fields.Char('Nombre lista')
    display_name = fields.Char('Nombre', compute="_compute_display_name")
    pricelist_id = fields.Many2one('product.pricelist', 'Lista')
    uom_id = fields.Many2one('uom.uom', 'Unidad predeterminada')
    product_templ_id = fields.Many2one('product.template', 'Producto')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    unit_price = fields.Float('Precio unitario', digits="Product Price", compute="_compute_all_unit_prices", store=False)
    is_special = fields.Boolean(string="Es prioritaria")
    branch_id = fields.Many2one('res.partner', string='Sucursal', related="pricelist_id.branch_id")

    def _compute_display_name(self):
        for record in self:
            if record.unit_price and record.name:
                record.display_name = f"{record.name} - {record.unit_price}"
            else:
                record.display_name = record.name

    def _compute_all_unit_prices(self):
        for line in self:
            line.unit_price = 0.0
            pricelist_id = line.pricelist_id
            product_id = line.product_templ_id

            if 'product_uom_id' in self.env.context:
                product_uom_id = self.env.context['product_uom_id']
            else:
                product_uom_id = line.product_templ_id.uom_id

            unit_price = pricelist_id._compute_price_rule(
                products=product_id,
                quantity=1,
                uom_id=product_uom_id,
                date=date.today())

            if product_id:
                line.unit_price = unit_price[product_id.id][0] or 0.0

    def name_get(self):
        result = []
        for record in self:
            name = ""
            if record.unit_price:
                name = f"{record.name} ({record.unit_price})"
            else:
                name = f"{record.name} ({record.currency_id})"

            result.append((record.id, name))
        return result

    def open_product_pricelist(self):
        origin_res_model = self.env.context.get('origin_res_model', False)
        origin_res_id = self.env.context.get('origin_res_id', False)

        return {
            'res_model': 'product.pricelist',
            'res_id': self.pricelist_id.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("product.product_pricelist_view").id,
            'context': {
                'is_filtered': True,
                'origin_res_model': origin_res_model,
                'origin_res_id': origin_res_id,
                'pricelist_id': self.pricelist_id.id
            }
        }
