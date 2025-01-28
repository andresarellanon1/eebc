from odoo import api, fields, models
from datetime import date
import logging
logger = logging.getLogger(__name__)


class ProductPricelistLine(models.Model):
    _name = 'product.pricelist.line'
    _description = 'Linea de lista de precios para producto'

    name = fields.Char('Nombre linea de lista por producto')
    display_name = fields.Char('Nombre', compute="_compute_display_name", store=False, readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Lista')
    uom_id = fields.Many2one('uom.uom', 'Unidad predeterminada', related="product_templ_id.uom_id")
    product_templ_id = fields.Many2one('product.template', string='Producto')
    currency_id = fields.Many2one('res.currency', string='Moneda', related="pricelist_id.currency_id")
    unit_price = fields.Float('Precio unitario', digits="Precio Unitario", compute="_compute_unit_price", store=False)
    is_special = fields.Boolean(string="Es prioritaria", related="pricelist_id.is_special")
    company_id = fields.Many2one('res.company', string='Empresa', related="pricelist_id.company_id")
    is_orphan = fields.Boolean(
        string='Línea Huérfana',
        compute='_compute_is_orphan',
        store=True,
        help='Indica si esta línea de lista de precios no está siendo utilizada en ninguna línea de pedido de venta.'
    )

    @api.depends()
    def _compute_is_orphan(self):
        """
        Determina si la línea de lista de precios no tiene relación con líneas de pedido de venta.
        1. Busca en todas las líneas de pedido de venta
        2. Verifica si alguna referencia esta línea de precio (campo `product_pricelist_id`)
        3. Marca como huérfana si no hay referencias
        - Utiliza `search_count` para optimizar consultas
        """
        sale_line_model = self.env['sale.order.line']
        for line in self:
            reference_count = sale_line_model.search_count([
                ('product_pricelist_id', '=', line.id)
            ])
            line.is_orphan = reference_count == 0

    def _compute_display_name(self):
        for record in self:
            record._compute_is_orphan()
            if record.unit_price and record.name and (not record.is_orphan):
                record.display_name = f"{record.name} - {record.unit_price} ({record.currency_id.name})"
            elif (not record.is_orphan) and (not record.pricelist_id):
                record.display_name = f"---Legacy {record.name} - {record.unit_price} ({record.currency_id.name})"
            elif (record.is_orphan) and (not record.pricelist_id):
                record.display_name = "---Orphan"
            else:
                record.display_name = record.name

    @api.depends('pricelist_id', 'product_templ_id', 'uom_id', 'currency_id')
    def _compute_unit_price(self):
        """
        Calcula el precio unitario basado en la lista de precios activa.
        1. Obtiene la lista de precios asociada a la línea
        2. Consulta la regla de precio aplicable para:
           - Plantilla de producto específica
           - Unidad de medida (UoM) configurada
           - Moneda actual
        3. Calcula para cantidad = 1
        4. Usa fecha vigente como referencia

        Returns:
            float: Precio unitario según lista de precios o 0.0
        """
        for line in self:
            line.unit_price = 0.0
            pricelist_id = line.pricelist_id
            product_id = line.product_templ_id
            unit_price = pricelist_id._compute_price_rule(
                products=product_id,
                quantity=1,
                uom_id=line.product_templ_id.uom_id,
                date=date.today())
            line.unit_price = unit_price[product_id.id][0] or 0.0

    def name_get(self):
        """
            Generates fancy display name
        """
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
        """
            Helper to launch filter product.pricelist.items action from the wizard-popup found openned to inspect this line.
        """
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
