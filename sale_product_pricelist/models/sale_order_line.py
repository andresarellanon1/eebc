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
        Custom Algorithm:
        Updates the price unit for the order line based on the pricelist.

        This algorithm ensures the correct pricelist is used by referencing the `order_id.target_currency_id`.
        It searches for the first match of an "Equivalent" pricelist in the target currency.

        Raises:
            ValidationError: If no suitable pricelist can be found for the product template in the correct currency.
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
        Computes the price unit for the order line using the company's currency.
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
        Finds the equivalent pricelist for the order line's product template in the correct currency.
        This method also ensures that the pricelist's company matches the company of the parent order.
        """
        for line in self:
            if line.product_id and (line.product_pricelist_id.currency_id.id != line.order_id.target_currency_id.id):
                # self.env.cr.commit()  # Save changes made to the parent order before continue
                product_pricelist = self.env["product.pricelist.line"].search([
                    ("product_templ_id", "=", line.product_template_id.id),
                    ("name", "=", line.product_pricelist_id.name),
                    ("currency_id", "=", line.order_id.target_currency_id.id),
                    ("company_id", "=", line.order_id.company_id.id)
                ], limit=1)
                logger.warning(f"== {line.product_template_id.name} ==")
                logger.warning(f"== {line.product_pricelist_id.name} ==")
                logger.warning(f"== {line.order_id.target_currency_id.name} ==")
                logger.warning(f"== {line.order_id.company_id.name} ==")
                logger.warning(f"== {product_pricelist.display_name} ==")
                if product_pricelist:
                    line.product_pricelist_id = product_pricelist
                else:
                    raise ValidationError(
                        f"No se pudo calcular prcio unitario debido a la divisa.\n"
                        f"No se encontró una lista de precios para el producto ‘{line.product_template_id.name}’"
                        f"con la moneda ‘{line.order_id.target_currency_id.name}’\n"
                        f"para la empresa ‘{line.company_id.name}’.\n"
                        f"Sin esta equivalencia, no es posible realizar el cambio de divisa.\n\n"
                        f"Por favor, elimine la línea de producto que causa este error de validación o cree la lista de precios correspondiente."
                    )

    def _get_price_unit(self, unit_price, safe_margin, source_currency, target_currency, company_id):
        """
        Helper method.
        Computes the price unit based on the given parameters and currency conversion.
        This method is solely responsible for adding the safe margin equivalent value in the order currency to the given prices.

        Args:
            unit_price (float): The unit price from the product pricelist.
            safe_margin (float): The safe margin for currency conversion.
            source_currency (record): The currency record representing the source currency for the safe margin field, likely the company currency.
            target_currency (record): The currency record representing the target currency.
            target_currency (record): The company of the line.

        Returns:
            float: The computed price unit in the target currency.
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
        Assigns the appropriate price list and price unit based on the currency and branch of the parent `order_id`.
        When no price list is present, the company currency is used against the order currency to compute the unit price.

        Raises:
            ValidationError: If a suitable price list cannot be found for the product template with the correct currency and branch.

        Returns:
            None
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
        Computes the price list for each order line based on default or customer-selected price lists.
        Dynamically retrieves the default pricelist from the user's company settings.

        For each order line:
        - Searches for the appropriate price list based on product, currency, and company.
        - Prioritizes the customer's selected price list if it exists, followed by the priority price list,
          and finally, the default price list.
        - If no product is selected, the method clears the price list field and exits.
        - If no price list is found for the product and currency, it raises a ValidationError.

        Raises:
            ValidationError: If no appropriate price list is found for the product and currency combination
                             or if the customer-selected or default price list is not available.
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
                msg = "No se pudo cargar la lista de precios predeterminada.\n"
                "No se encontró una lista de precios predeterminada para:\n"
                f"producto ‘[{line.product_template_id.default_code}] {line.product_template_id.name}’ con la moneda ‘{line.order_id.target_currency_id.name}’.\n"
                "Para continuar, cree una lista de precios predeterminada que cumpla con los requisitos o desactive esta validación."
                raise ValidationError(msg)
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
                raise ValidationError("No se pudo cargar la lista de precios del cliente ni la predeterminada para:\n"
                                      f"producto ‘[{line.product_template_id.default_code}] {line.product_template_id.name}’ con la moneda ‘{line.order_id.target_currency_id.name}’.\n"
                                      "Para continuar, cree una lista de precios que cumpla con los requisitos o desactive esta validación.")
            # === Write === #
            line.product_pricelist_id = product_pricelist_id

    def _compute_line_uom_factor(self):
        """
               ===> Critical Warning for Developers <===
        Calling this method more than once with identical values for both 'default' and 'selected' unit of measures (UoM) can lead to a severe bug.
        Consequently, the unit price will undergo exponential multiplication with each subsequent invocation of this method.

        It is imperative to diligently monitor any code segment that interacts with this model to detect and prevent occurrences of this bug.
        Should such circumstances arise unavoidably, consider implementing a flag within this model:
        - Use a flag in your code to prevent the method from being invoked successively with the same combination of 'default' and 'selected' UoM values.
        - You'll probably need to add a new field to the line to store whether the last time a combination of UoMs was computed, it was 'default' to 'selected' or 'selected' to 'default'.
        - I don't implement this by default as it would cause unnecessary overhead for my use cases.
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
