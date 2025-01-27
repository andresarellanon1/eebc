import logging
from odoo import models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_product_pricelist(self):
        """
            Override
            Implemented custom method to recompute price unit per line.
            Uses the pricelist lines of the product template to find the price unit with the most priority in the accurate currency and branch.
        """
        for order in self:
            for line in order.order_line:
                if line.product_pricelist_id.currency_id.id != line.order_id.target_currency_id.id:
                    product_pricelist = line._find_equivalent_pricelist()
                    if not product_pricelist:
                        raise ValidationError(
                            f"No se pudo calcular prcio unitario debido a la divisa.\n"
                            f"No se encontró una lista de precios para el producto ‘{line.product_template_id.name}’"
                            f"con la moneda ‘{line.order_id.target_currency_id.name}’\n"
                            f"para la empresa ‘{line.company_id.name}’.\n"
                            f"Sin esta equivalencia, no es posible realizar el cambio de divisa.\n\n"
                            f"Por favor, elimine la línea de producto que causa este error de validación o cree la lista de precios correspondiente."
                        )
                line.product_pricelist_id = product_pricelist
                line._compute_pricelist_price_unit()
