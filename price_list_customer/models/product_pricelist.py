import logging
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_special = fields.Boolean(default=False,
                                string="Es especial",
                                help="Marcar esta casilla asegura que ésta lista de precios no se muestre en el menú flotante de selección en las líneas de orden de venta. Marca esta casilla asegura que ésta lista de precios se muestre en el campo de selección de listas de precio especial para clientes.")
