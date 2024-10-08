from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo import models, api, fields
import logging
from datetime import date
logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    locked_currency_id = fields.Many2one(
        string="Divisa",
        help='Divisa. Depende de la divisa de la orden padre.',
        comodel_name='res.currency'
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleOrderLine, self).create(vals_list)
        for line in lines:
            line.locked_currency_id = line.order_id.locked_currency_id

        return lines

    @api.onchange("product_id")
    def product_id_change(self):
        for line in self:
            line.locked_currency_id = line.order_id.locked_currency_id
            if line.product_template_id:
                line.product_template_id.get_product_pricelist()

            line._select_default_pricelist()

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.safe_margin')
    def _compute_price_unit(self):
        super(SaleOrderLine, self)._compute_price_unit()

        for line in self:
            line._compute_pricelist_price_unit()

    @api.onchange("product_pricelist_id")
    def product_pricelist_id_change(self):
        for line in self:
            line._compute_pricelist_price_unit()

    def _compute_pricelist_price_unit(self):
        """
        Assigns the appropriate price list and price unit based on the currency of the parent order_id.
        This method ensures that each order line has the correct price list and price unit assigned based on the currency of the parent order.
        It manages this regardless of other method invocations and computations.
        When no price list is present, the company currency is used against the order currency to compute the unit price.

        Args:
            self: The recordset of order lines.
        Raises:
            ValidationError: If a suitable price list cannot be found for the product template with the correct currency.
        Returns:
            None
        """

        def _update_price_for_pricelist(line):
            """
            Updates price unit for the order line based on the pricelist.

            Args:
                line: The order line.

            Returns:
                None

            Raises:
                ValidationError: If a suitable price list cannot be found for the product template with the correct currency.
            """
            if line.product_pricelist_id.currency_id != line.order_id.locked_currency_id:
                product_pricelist = _find_equivalent_pricelist(line)
                if not product_pricelist:
                    raise ValidationError(
                        f"No se pudo calcular el cambio de divisa. No se encontró una lista de precios para el producto ‘{line.product_template_id.name}’ con la moneda ‘{line.order_id.locked_currency_id.name}’. Sin esta equivalencia, no es posible realizar el cambio de divisa. Por favor, elimine la línea de producto que causa este error de validación o cree la lista de precios correspondiente."
                    )

                line.product_pricelist_id = product_pricelist

            line.price_unit = _compute_price_unit(unit_price=line.product_pricelist_id.unit_price,
                                                  safe_margin=line.order_id.safe_margin,
                                                  source_currency=self.env.company.currency_id,
                                                  target_currency=line.order_id.locked_currency_id
                                                  )

            if line.product_pricelist_id.uom_id.id != line.product_uom.id:
                line._compute_line_uom_now()

        def _update_price_for_company_currency(line):
            """
            Updates price unit for the order line using company currency.

            Args:
                line: The order line.

            Returns:
                None
            """
            unit_price = line.price_unit

            if line.order_id.locked_currency_id.id != line.locked_currency_id.id:
                unit_price = line.locked_currency_id._convert(
                    unit_price,
                    line.order_id.locked_currency_id,
                    self.env.company,
                    date.today(),
                    round=False,
                )

            line.price_unit = _compute_price_unit(unit_price=unit_price,
                                                  safe_margin=line.order_id.safe_margin,
                                                  source_currency=self.env.company.currency_id,
                                                  target_currency=line.order_id.locked_currency_id)

            if line.product_pricelist_id.uom_id.id != line.product_uom.id:
                line._compute_line_uom_now()

        def _find_equivalent_pricelist(line):
            """
            Finds the equivalent pricelist for the order line's product template with the correct currency,
            and also checks if the pricelist location matches the current company where the user is logged in.

            Args:
                line: The sale order line for which the pricelist needs to be found.

            Returns:
                The equivalent product pricelist line based on the product template, 
                pricelist name, order currency, and the company location.
            """
            return self.env["product.pricelist.line"].search(
                [
                    ("product_templ_id", "=", line.product_template_id.id),
                    ("name", "=", line.product_pricelist_id.name),
                    ("currency_id", "=", line.order_id.locked_currency_id.id),
                    ("pricelist_id.location", "=", self.env.company.id)
                ],
                limit=1
            )

        def _compute_price_unit(unit_price, safe_margin, source_currency, target_currency):
            """
            Computes the price unit based on the given parameters and currency conversion.
            This sub-method is single handedly resposable for adding the safe margin equivalent value in order currency to the given prices.

            Args:
                unit_price (float): The unit price from the product pricelist.
                safe_margin (float): The safe margin for currency conversion.
                source_currency (record): The currency record representing the source currency for the safe margin field, likely the company currency.
                target_currency (record): The currency record representing the target currency.

            Returns:
                float: The computed price unit in the target currency.
            """
            def convert_currency(amount, from_currency, to_currency):
                return from_currency._convert(
                    amount,
                    to_currency,
                    self.env.company,
                    date.today(),
                    round=False,
                )

            if source_currency == target_currency:  # MXN TO MXN BUT PRODUCT PURCHASED ON USD by last supplier or main supplier
                return unit_price

            # Convert "safe margin" if source and target currencies differ, USD TO MXN OR MXN TO USD.
            added_value = convert_currency(unit_price * safe_margin, source_currency, target_currency)
            return unit_price + added_value

        # Main workflow of this method
        for line in self:
            if not line.product_template_id:
                line.price_unit = 0.00
                continue

            if line.product_pricelist_id:
                _update_price_for_pricelist(line)
            else:
                _update_price_for_company_currency(line)

    def _select_default_pricelist(self):
        """
        Computes the price list for each order line based on default or customer-selected price lists.
        This method no longer hardcodes the default price list; instead, it dynamically retrieves the default 
        pricelist from the user's company settings. Additionally, it ensures that the search includes the 
        company (location) where the user is currently logged in.

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
        def _get_pricelist(product_template, pricelist_id, currency, company):
            return self.env["product.pricelist.line"].search(
                [
                    ("product_templ_id", "=", product_template),
                    ("pricelist_id", "=", pricelist_id),
                    ("currency_id", "=", currency),
                    ("pricelist_id.location", "=", company)
                ],
                limit=1)

        def _get_default_pricelist(product_template, pricelist_id, currency):
            return self.env["product.pricelist.line"].search(
                [
                    ("product_templ_id", "=", product_template),
                    ("pricelist_id", "=", pricelist_id),
                    ("currency_id", "=", currency)
                ],
                limit=1)

        for line in self:
            if not line.product_template_id:
                line.product_pricelist_id = False
                continue

            product_pricelist_id = False

            default_pricelist_id = self.env.user.company_id.default_product_pricelist_id.id
            actual_company = self.env.company.id

            default_pricelist_id = int(default_pricelist_id) if default_pricelist_id else False
            default_product_pricelist_id = _get_default_pricelist(line.product_template_id.id, default_pricelist_id, line.order_id.locked_currency_id.id) if default_pricelist_id else False

            priority_customer_selected_pricelist = _get_pricelist(line.product_template_id.id, line.order_id.partner_id.priority_pricelist_id.id, line.order_id.locked_currency_id.id, actual_company) if line.order_id.partner_id.priority_pricelist_id else False

            customer_selected_pricelist = _get_pricelist(line.product_template_id.id, line.order_id.partner_id.property_product_pricelist.id, line.order_id.locked_currency_id.id, actual_company) if line.order_id.partner_id.property_product_pricelist else False

            if (not default_product_pricelist_id) and (not customer_selected_pricelist) and (not priority_customer_selected_pricelist):
                msg = "No se pudo cargar la lista de precios predeterminada.\n"
                "No se encontró una lista de precios predeterminada para:\n"
                f"producto ‘[{line.product_template_id.default_code}] {line.product_template_id.name}’ con la moneda ‘{line.order_id.currency_id.name}’.\n"
                "Para continuar, cree una lista de precios predeterminada que cumpla con los requisitos o desactive esta validación."
                raise ValidationError(msg)

            if priority_customer_selected_pricelist and (not product_pricelist_id):
                product_pricelist_id = _get_pricelist(line.product_template_id.id, priority_customer_selected_pricelist.name, priority_customer_selected_pricelist.currency_id.id, actual_company)

            if customer_selected_pricelist and (not product_pricelist_id):
                # Search for the price list line that matches the customer-selected price list
                product_pricelist_id = _get_pricelist(line.product_template_id.id, customer_selected_pricelist.name, customer_selected_pricelist.currency_id.id, actual_company)

            if default_product_pricelist_id and (not product_pricelist_id):
                product_pricelist_id = default_product_pricelist_id

            if not product_pricelist_id:
                raise ValidationError("No se pudo cargar la lista de precios del cliente ni la predeterminada para:\n"
                                      f"producto ‘[{line.product_template_id.default_code}] {line.product_template_id.name}’ con la moneda ‘{line.order_id.currency_id.name}’.\n"
                                      "Para continuar, cree una lista de precios que cumpla con los requisitos o desactive esta validación.")

            line.product_pricelist_id = product_pricelist_id

            line._compute_pricelist_price_unit()

    def _compute_line_uom_now(self):
        """Attention: Critical Warning for Developers
        Calling this method more than once with identical values for both 'default' and 'selected' unit of measures (uom) can lead to a severe and complex bug.

        Consequently, the unit price will undergo exponential multiplication with each subsequent invocation of this method. Removing the logger associated with this method is strongly discouraged.

        It is imperative to diligently monitor any code segment that interacts with this model to detect and prevent occurrences of this bug.

        Exercise caution when calling this method, ensuring it is not invoked consecutively. For instance, avoid scenarios where multiple computed fields trigger this method simultaneously during a single action.

        Should such circumstances arise unavoidably, consider implementing a flag within this model. Utilize this flag in your code to prevent the method from being invoked successively with the same combination of 'default' and 'selected' uom values.
        """
        for line in self:
            line.locked_currency_id = line.order_id.locked_currency_id

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
        """Compute the displayed unit price for a given line."""
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if self.product_pricelist_id and self.product_pricelist_id.pricelist_id.discount_policy != 'with_discount':
            base_price = self._get_pricelist_price_before_discount()
            return max(base_price, pricelist_price)

        return pricelist_price

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.product_pricelist_id.unit_price

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.product_pricelist_id.unit_price
