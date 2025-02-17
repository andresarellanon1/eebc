from odoo import models, api, fields
from datetime import date
from odoo.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_pricelist_id = fields.Many2one("product.pricelist.line", string="Lista precio")
    pricelist_unit_price = fields.Float('Precio de lista de precio', digits="Product Price", readonly=True, related="product_pricelist_id.unit_price")

    @api.onchange("product_pricelist_id")
    def product_pricelist_id_change(self):
        logger.warning('El pricelist es: %s', self.product_pricelist_id.id)
        logger.warning('El pricelist es: %s', self.product_pricelist_id.name)
        
        if self.product_pricelist_id:
            self.product_pricelist_id.imprimir_registros()
            
        for line in self:
            line._compute_pricelist_price_unit()

    @api.onchange("product_id")
    def product_id_change(self):
        """
        Overwrite the method to check for a partner. If no partner is selected, we avoid showing a misleading error message.

        The error message is only shown when there is an actual problem, such as when a product is not found in any pricelist
        valid for the customer and company.
        """
        for line in self:
            if not line.order_id.partner_id:
                raise ValidationError("El cliente es requerido antes de capturar las lineas.")
            line._select_default_pricelist()
            line._compute_pricelist_price_unit()
            line._select_equivalent_pricelist()

    @api.depends_context('company')
    @api.depends('company_id', 'product_id', 'product_uom', 'product_uom_qty', 'product_pricelist_id', 'order_id.safe_margin', 'order_id.partner_id')
    def _compute_price_unit(self):
        """
        Overwrite the method to compute the price unit of the line using a custom algorithm.

        To ensure the input of the algorithm is always consistent with the expected value, we call `super()`.
        This guarantees that the value used is the same as the default value Odoo assigns to the `price_unit` field
        of the `sale.order.line`.
        """
        super(SaleOrderLine, self)._compute_price_unit()
        for line in self:
            line._compute_pricelist_price_unit()

    def _update_price_for_pricelist(self):
        """
        Actualiza el precio unitario de la línea de pedido basado en la lista de precios.

        Utiliza la moneda objetivo del pedido (`order_id.target_currency_id`) para identificar
        y aplicar la lista de precios equivalente en la moneda correspondiente.

        Raises:
            ValidationError: Si no se encuentra una lista de precios válida para la moneda objetivo.
        """
        for line in self:
            line.price_unit = line._get_price_unit(unit_price=line.product_pricelist_id.unit_price,
                                                   safe_margin=line.order_id.safe_margin,
                                                   source_currency=line.company_id.currency_id,
                                                   target_currency=line.order_id.target_currency_id,
                                                   company_id=line.company_id)
            if line.product_pricelist_id.uom_id.id != line.product_uom.id:
                line._compute_line_uom_factor()

    def _update_price_for_company_currency(self):
        """
        Calcula el precio unitario de la línea de pedido utilizando la moneda de la compañía.

        Realiza conversión de divisa cuando la moneda objetivo difiere de la moneda de la compañía,
        aplicando el margen de seguridad configurado en el pedido.
        """
        for line in self:
            unit_price = line.price_unit
            if line.order_id.target_currency_id.id != line.order_id.target_currency_id.id:
                unit_price = line.order_id.target_currency_id._convert(
                    unit_price,
                    line.order_id.target_currency_id,
                    line.company_id,
                    date.today(),
                    round=False)
            line.price_unit = line._get_price_unit(unit_price=unit_price,
                                                   safe_margin=line.order_id.safe_margin,
                                                   source_currency=line.company_id.currency_id,
                                                   target_currency=line.order_id.target_currency_id,
                                                   company_id=line.company_id)
            if line.product_pricelist_id.uom_id.id != line.product_uom.id:
                line._compute_line_uom_factor()

    def _select_equivalent_pricelist(self):
        """
        Busca la lista de precios equivalente en la moneda objetivo del pedido.

        Verifica coincidencia de:
        - Plantilla del producto
        - Nombre de la lista de precios
        - Moneda objetivo
        - Compañía del pedido

        Raises:
            ValidationError: Si no existe una lista de precios con los criterios requeridos.
        """
        for line in self:
            if line.product_id and (line.product_pricelist_id.currency_id.id != line.order_id.target_currency_id.id):
                product_pricelist = self.env["product.pricelist.line"].search([
                    ("product_templ_id", "=", line.product_template_id.id),
                    ("name", "=", line.product_pricelist_id.name),
                    ("currency_id", "=", line.order_id.target_currency_id.id),
                    ("company_id", "=", line.order_id.company_id.id)
                ], limit=1)
                if product_pricelist:
                    line.product_pricelist_id = product_pricelist
                else:
                    raise ValidationError(
                        f"No se pudo calcular el precio unitario por discrepancia cambiaria.\n"
                        f"Producto: ‘{line.product_template_id.name}’\n"
                        f"Moneda requerida: {line.order_id.target_currency_id.name}\n"
                        f"Compañía: {line.company_id.name}\n\n"
                        "Acciones requeridas:\n"
                        "1. Elimine la línea problemática\n"
                        "2. Cree una lista de precios equivalente\n"
                        "3. Verifique configuraciones cambiarias"
                    )

    def _get_price_unit(self, unit_price, safe_margin, source_currency, target_currency, company_id):
        """
        Calcula el precio unitario aplicando conversión monetaria y margen de seguridad.

        Args:
            unit_price (float): Precio base de la lista de precios
            safe_margin (float): Margen porcentual para fluctuaciones cambiarias
            source_currency (record): Moneda origen (usualmente moneda de la compañía)
            target_currency (record): Moneda objetivo del pedido
            company_id (record): Compañía para contexto de conversión

        Returns:
            float: Precio unitario convertido con margen aplicado
        """
        def convert_currency(amount, from_currency, to_currency, company_id):
            return from_currency._convert(
                amount,
                to_currency,
                company_id,
                date.today(),
                round=False,
            )
        # NOTE: SAME CURRENCY BUT PRODUCT PURCHASED ON LOCKED CURRENCY by last supplier or main supplier.
        if source_currency == target_currency:
            return unit_price
        # NOTE: Convert "safe margin" if source and target currencies differ, e.g. USD TO MXN OR MXN TO USD.
        added_value = convert_currency(unit_price * safe_margin, source_currency, target_currency, company_id)
        return unit_price + added_value

    def _compute_pricelist_price_unit(self):
        """
        Determina el precio unitario final usando listas de precios o moneda de compañía.

        Prioridad de cálculo:
        1. Lista de precios asignada
        2. Conversión directa de moneda de compañía

        Raises:
            ValidationError: Si no se puede determinar un método de cálculo válido
        """
        for line in self:
            if not line.product_template_id:
                line.price_unit = 0.00
                continue
            if line.product_pricelist_id:
                self._update_price_for_pricelist()
            else:
                self._update_price_for_company_currency()

    def _select_default_pricelist(self):
        """
        Selecciona la lista de precios aplicable usando jerarquía configurada.

        Prioridad de selección:
        1. Lista prioritaria del cliente
        2. Lista estándar del cliente
        3. Lista predeterminada de la compañía

        Raises:
            ValidationError: Si no se encuentra ninguna lista de precios compatible
        """
        def _get_pricelist_line(product_template, pricelist_id, currency, company_id):
            # It doesn't matter because the find equivalent will fix any currency missmatch
            eq_pricelist_ids = self.env["product.pricelist"].search([("name", "=", pricelist_id.name)])
            return self.env["product.pricelist.line"].search([("product_templ_id", "=", product_template.id),
                                                              ("pricelist_id", "in", eq_pricelist_ids.ids),
                                                              ("currency_id", "=", currency.id),
                                                              ("company_id", "=", company_id.id)],
                                                             limit=1)  # RETURN ONLY 1
        for line in self:
            if not line.product_template_id:
                line.product_pricelist_id = False
                continue
            product_pricelist_id = False
            # Pricelists declarations
            default_pricelist_id = line.company_id.selected_product_pricelist_id
            priority_customer_selected_pricelist = line.order_id.partner_id.priority_pricelist_id
            customer_selected_pricelist = line.order_id.partner_id.property_product_pricelist
            # NOTE: Asseert at least one of the 3 pricelist options available
            if (not default_pricelist_id) and (not customer_selected_pricelist) and (not priority_customer_selected_pricelist):
                raise ValidationError(
                    "Fallo en carga de lista de precios predeterminada.\n"
                    f"Producto: [{line.product_template_id.default_code}] {line.product_template_id.name}\n"
                    f"Moneda objetivo: {line.order_id.target_currency_id.name}\n\n"
                    "Soluciones:\n"
                    "1. Cree una lista de precios compatible\n"
                    "2. Desactive validaciones cambiarias\n"
                    "3. Verifique configuraciones del cliente"
                )
            if priority_customer_selected_pricelist and (not product_pricelist_id):
                # NOTE: Search for the price list line that matches the priority-selected price list
                product_pricelist_id = _get_pricelist_line(product_template=line.product_template_id,
                                                           pricelist_id=priority_customer_selected_pricelist,
                                                           currency=priority_customer_selected_pricelist.currency_id,
                                                           company_id=line.company_id)
            if customer_selected_pricelist and (not product_pricelist_id):
                # NOTE: Search for the price list line that matches the customer-selected price list
                product_pricelist_id = _get_pricelist_line(product_template=line.product_template_id,
                                                           pricelist_id=customer_selected_pricelist,
                                                           currency=customer_selected_pricelist.currency_id,
                                                           company_id=line.company_id)
            if default_pricelist_id and (not product_pricelist_id):
                # NOTE: default ...
                product_pricelist_id = _get_pricelist_line(product_template=line.product_template_id,
                                                           pricelist_id=default_pricelist_id,
                                                           currency=customer_selected_pricelist.currency_id,
                                                           company_id=line.company_id)
            if not product_pricelist_id:
                # NOTE: Undefined behavior
                raise ValidationError(
                    "Inconsistencia en listas de precios disponibles.\n"
                    f"Producto: [{line.product_template_id.default_code}] {line.product_template_id.name}\n"
                    f"Moneda objetivo: {line.order_id.target_currency_id.name}\n\n"
                    "Revisar:\n"
                    "- Listas prioritarias del cliente\n"
                    "- Configuración cambiaria de la compañía\n"
                    "- Existencia de precios base para el producto"
                )
            # === Write === #
            line.product_pricelist_id = product_pricelist_id

    def _compute_line_uom_factor(self):
        """
        Ajusta el precio unitario basado en la relación de unidades de medida.

        ! ADVERTENCIA CRÍTICA !
        Llamadas consecutivas con mismas UoMs pueden causar multiplicaciones exponenciales.
        Implementar controles externos para prevenir invocaciones redundantes.
        """
        for line in self:
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
                return
            if line.product_pricelist_id and line.product_id and line.product_uom and line.product_uom_qty and line.price_unit:
                default_uom = line.product_pricelist_id.uom_id
                selected_uom = line.product_uom
                factor = selected_uom._compute_quantity(1, default_uom)
                if factor:
                    line.price_unit = line.price_unit * factor

    def _get_display_price(self):
        """
        Overwritten
        Compute the displayed unit price for a given line.
        """
        self.ensure_one()
        pricelist_price = self._get_pricelist_price()
        if self.product_pricelist_id and self.product_pricelist_id.pricelist_id.discount_policy != 'with_discount':
            base_price = self._get_pricelist_price_before_discount()
            return max(base_price, pricelist_price)
        return pricelist_price

    def _get_pricelist_price(self):
        """
        Overwritten
        Compute the price given by the pricelist for the given line information.

        Returns:
            float: The product sales price in the order currency (without taxes).
        """
        self.ensure_one()
        self.product_id.ensure_one()
        return self.product_pricelist_id.unit_price

    def _get_pricelist_price_before_discount(self):
        """
        Overwritten
        Compute the price used as base for the pricelist price computation.

        Returns:
            float: The product sales price in the order currency (without taxes).
        """
        self.ensure_one()
        self.product_id.ensure_one()
        return self.product_pricelist_id.unit_price
