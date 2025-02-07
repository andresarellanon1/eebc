import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductPricelist, self).create(vals_list)
        for record in records:
            record._compute_product_pricelist_lines()
        return records

    def write(self, vals):
        res = super(ProductPricelist, self).write(vals)
        if 'item_ids' in vals:
            for line in self:
                line._compute_product_pricelist_lines()
        return res
        
    def action_update_pricelist(self):
    # Aquí va la lógica para actualizar la lista de precios
    for record in self:
        # record._compute_product_pricelist_lines()
    return True

    def _compute_product_pricelist_lines(self):
        """
        Actualiza las líneas de lista de precios relacionadas en productos y plantillas.

        Procesa recursivamente los items de la lista de precios según su alcance:
        1. Variantes de producto directas(`0_product_variant`):
           - Actualiza plantillas vinculadas a variantes específicas
        2. Productos directos (`1_product`):
           - Recalcula precios en plantillas asociadas explícitamente
        3. Categorías de producto (`2_product_category`):
           - Afecta todas las plantillas dentro de la categoría configurada
        4. Alcance global (`3_global`):
           - Procesa todas las plantillas existentes en la base de datos
           - Opera en bloques de 100 registros para optimizar memoria
           - Realiza commit tras cada bloque y limpia la caché del entorno

        Flujo:
        - Identifica items por tipo de alcance
        - Dispara recomputación en cascada de precios
        - Maneja datasets masivos con procesamiento batch

        Efectos Secundarios:
        - Genera commits transaccionales parciales
        - Limpia caché del entorno periódicamente
        - Puede afectar rendimiento en bases grandes

        Uso típico:
        Llamado durante cambios en listas de precios para propagar actualizaciones
        """
        for pricelist in self:
            items_direct_relation_variant = self.env['product.pricelist.item'].search([('applied_on', '=', '0_product_variant'), ('pricelist_id', '=', pricelist.id)])
            items_direct_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '1_product'), ('pricelist_id', '=', pricelist.id)])
            items_category_relation = self.env['product.pricelist.item'].search([('applied_on', '=', '2_product_category'), ('pricelist_id', '=', pricelist.id)])
            items_all_stock = self.env['product.pricelist.item'].search([('applied_on', '=', '3_global'), ('pricelist_id', '=', pricelist.id)])

            if items_direct_relation.product_tmpl_id:
                product_template = self.env["product.template"].search([('id', '=', items_direct_relation.product_tmpl_id.id)])
                product_template._compute_product_pricelist_line_ids()

            if items_direct_relation_variant.product_id:
                product = self.env["product.product"].search([('id', '=', items_direct_relation.product_id.id)])
                product.product_tmpl_id._compute_product_pricelist_line_ids()

            if items_category_relation.categ_id:
                for category in items_category_relation.categ_id:
                    product_templates = self.env["product.template"].search([('categ_id', '=', category.id)])
                    product_templates._compute_product_pricelist_line_ids()
                    
            if items_all_stock:
                product_templates = self.env["product.template"].search([]).with_prefetch()
                batch_size = 100

                for i in range(0, len(product_templates), batch_size):
                    batch = product_templates[i:i + batch_size]
                    batch._compute_product_pricelist_line_ids()
                    self.env.cr.commit()
                    self.env.clear()  # Clear the environment cache to free memory

    @api.depends('item_ids')
    def _compute_filtered_item_ids(self):
        for pricelist in self:
            pricelist.filtered_item_ids = False
            origin_res_model = pricelist.env.context.get('origin_res_model', False)
            origin_res_id = pricelist.env.context.get('origin_res_id', False)
            pricelist_id = pricelist.env.context.get('pricelist_id', False)

            if not origin_res_model or not origin_res_id or not pricelist_id:
                return

            if origin_res_model == 'product.template':
                pricelist.filtered_item_ids = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist_id),
                    ('product_tmpl_id', '=', origin_res_id),
                    ('applied_on', '=', '1_product')
                ])

            elif origin_res_model == 'product.product':
                pricelist.filtered_item_ids = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist_id),
                    ('product_id', '=', origin_res_id),
                    ('applied_on', '=', '0_product_variant')
                ])

    def inverse_filtered_item_ids(self):
        self.item_ids = self.filtered_item_ids | self.item_ids

    filtered_item_ids = fields.One2many(
        comodel_name='product.pricelist.item',
        inverse_name='pricelist_id',
        string="Pricelist Rules",
        domain=[
            '&',
            '|', ('product_tmpl_id', '=', None), ('product_tmpl_id.active', '=', True),
            '|', ('product_id', '=', None), ('product_id.active', '=', True),
        ],
        copy=True, compute="_compute_filtered_item_ids", inverse='inverse_filtered_item_ids')
