from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date
import logging

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    landed_date = fields.Date()

    supplier_history = fields.One2many(
        "product.supplierinfo_history",
        "product_template_id",
        string="Historial de proveedores",
        help="Historial de relación proveedor-compra para este producto",
        readonly=True
    )

    main_supplier_id = fields.Many2one(
        "product.supplierinfo",
        string="Proveedor principal",
        help='Se selecciona desde el registro de proveedor.',
        compute="_compute_main_supplier_id",
        store=True,
        readonly=True,
    )

    main_supplier_last_price = fields.Float(
        string="Último costo proveedor principal",
        help='Se computa desde el registro de proveedor. Cuando la divisa es diferente a la del costo base, se utiliza este campo para re-computar el costo base al tipo de cambio del dia en curso.',
        compute="_compute_main_supplier_last_price",
        store=True,
        digits="Product Price",
        readonly=True,
    )

    main_supplier_last_order_currency_id = fields.Many2one(
        string="Divisa proveedor principal",
        help='Se computa desde el registro de proveedor.',
        comodel_name='res.currency',
        compute="_compute_main_supplier_last_order_currency_id",
        store=True,
        readonly=True
    )

    last_supplier_id = fields.Many2one(
        "product.supplierinfo",
        string="Ultimo proveedor",
        help='Se computa desde el historial de proveedores.',
        compute="_compute_last_supplier_id",
        store=True,
        readonly=True,
    )

    last_supplier_datetime = fields.Datetime(string="Fecha ultimo proveedor", readonly=True, compute="_compute_last_supplier_datetime")

    last_supplier_last_price = fields.Float(
        string="Último costo del ultimo proveedor",
        help='Se computa desde el registro de proveedor. Es el ultimo precio del proveedor mas reciente, no necesariamente el principal.',
        compute="_compute_last_supplier_last_price",
        digits="Product Price",
        store=True,
        readonly=True,
    )

    last_supplier_last_order_currency_id = fields.Many2one(
        string="Divisa del ultimo proveedor",
        help='Se computa desde el registro de proveedor.',
        comodel_name='res.currency',
        compute="_compute_last_supplier_last_order_currency_id",
        store=True,
        readonly=True
    )

    accounting_standard_price = fields.Float(
        string="Costo contable",
        help='Se computa desde el historico de ventas. Ignora los proveedores, usa directamente todas las compras que contengan este producto.',
        compute="_compute_accounting_standard_price",
        digits="Product Price",
        store=True,
        readonly=True,
    )

    @api.depends("seller_ids.is_main_supplier")
    def _compute_main_supplier_id(self):
        for template in self:
            if template.seller_ids:
                template.main_supplier_id = template.seller_ids.filtered(
                    lambda s: s.is_main_supplier
                )[:1]
                # template._compute_list_price()

    @api.depends("main_supplier_id.price")
    def _compute_main_supplier_last_price(self):
        for template in self:
            if template.main_supplier_id:
                template.main_supplier_last_price = template.main_supplier_id.price
                # template._compute_list_price()

    @api.depends("main_supplier_id.currency_id")
    def _compute_main_supplier_last_order_currency_id(self):
        for template in self:
            if template.main_supplier_id:
                template.main_supplier_last_order_currency_id = template.main_supplier_id.currency_id
                # template._compute_list_price()

    @api.depends("supplier_history")
    def _compute_last_supplier_id(self):
        for template in self:
            if template.supplier_history:
                sorted_history = template.supplier_history.sorted(key=lambda r: r.datetime, reverse=True)
                template.last_supplier_id = sorted_history[0].product_supplierinfo_id
                # template._compute_list_price()

    @api.depends("supplier_history")
    def _compute_last_supplier_datetime(self):
        for template in self:
            template.last_supplier_datetime = False
            if template.supplier_history:
                sorted_history = template.supplier_history.sorted(key=lambda r: r.datetime, reverse=True)
                if sorted_history[0].datetime:
                    template.last_supplier_datetime = sorted_history[0].datetime
                # template._compute_list_price()

    @api.depends("last_supplier_id.price")
    def _compute_last_supplier_last_price(self):
        for template in self:
            if template.last_supplier_id:
                template.last_supplier_last_price = template.last_supplier_id.price
                # template._compute_list_price()

    @api.depends("last_supplier_id.currency_id")
    def _compute_last_supplier_last_order_currency_id(self):
        for template in self:
            if template.last_supplier_id:
                template.last_supplier_last_order_currency_id = template.last_supplier_id.currency_id
                # template._compute_list_price()

    def _compute_safe_margin_add(self):
        for product in self:
            supplier_currency = None
            added_value = 0.00

            safe_margin = self.env["ir.config_parameter"].sudo().get_param("sale.safe_margin")

            if product.main_supplier_id:
                supplier_currency = product.main_supplier_id.currency_id
                supplier_last_price = product.main_supplier_last_price
            elif product.last_supplier_id:
                supplier_currency = product.last_supplier_id.currency_id
                supplier_last_price = product.last_supplier_last_price

            if supplier_currency:
                if supplier_currency.id != self.env.company.currency_id.id:
                    added_value = supplier_last_price * float(safe_margin)
                # TODO: or else raise an error i guess, maybe? yes? no?
                # else:
                    # raise ValidationError(f"Proveedor sin divisa: {product.last_supplier_id}")

            return added_value

    def _compute_list_price(self):
        """
        Computes the product template list price based on the supplier's price (main supplier if available, otherwise last supplier).
        If necessary, converts the supplier's price from their currency to the product's cost currency.
        Applies a safe margin addition if the main supplier is used.

        The process involves:
        1. Retrieving the price and currency of the relevant supplier.
        2. Converting the price to the product's cost currency if needed.
        3. Updating the product's list price.

        If no suppliers are available, sets the list price to 0.00.
        """

        def convert_currency(amount, from_currency, to_currency):
            return from_currency._convert(
                amount,
                to_currency,
                self.env.company,
                date.today(),
                round=False,
            )

        for product in self:
            if not product.main_supplier_id and not product.last_supplier_id:
                product.list_price = 0.00
                return

            supplier = product.main_supplier_id if product.main_supplier_id else product.last_supplier_id
            price = supplier.price
            currency_id = supplier.currency_id

            if price is not None:
                if currency_id.id != self.env.company.currency_id.id:
                    price = convert_currency(price, currency_id, self.env.company.currency_id)

                safe_added = self._compute_safe_margin_add()
                product.list_price = price + safe_added

    def _compute_standard_price(self, landed_date=False):
        """
               WARNING:

               USED FOR STOCK VALUATION LAYERS WITH CUSTOMS LANDED DATE CONVERSION RATE.
               DO NOT USE THIS FIELD FOR ACCOUNTING ANYMORE.

               Computes the product template standard cost given the supplier(main or last if not main selected) price and currency.
               Converts currency for the passed date and saves the last instance of the date for follow up calls.
               The date is only passed when called from a purhcase document confirmation action.

               Args:
                   landed_date: The date of the stock.landed.cost record related to the purhcase.order.line
               Returns:
                   None

        """
        for product in self:

            if not landed_date:
                landed_date = product.landed_date
            else:
                product.landed_date = landed_date

            if (not product.main_supplier_id) and (not product.last_supplier_id):
                product.standard_price = 0.00
                return

            # Main supplier selected
            if product.main_supplier_id:
                price = product.main_supplier_id.price
                main_supplier_currency_id = product.main_supplier_id.currency_id

                if main_supplier_currency_id.id != product.cost_currency_id.id:
                    price = main_supplier_currency_id._convert(
                        price,
                        product.cost_currency_id,
                        self.env.company,
                        landed_date,  # Usar dia del pedimento
                        round=False,
                    )

                product.standard_price = price
                return

                # No main supplier selected
            if product.last_supplier_id:
                price = product.last_supplier_id.price
                last_supplier_currency_id = product.last_supplier_id.currency_id

                if last_supplier_currency_id.id != product.cost_currency_id.id:
                    price = last_supplier_currency_id._convert(
                        price,
                        product.cost_currency_id,
                        self.env.company,
                        landed_date,  # Usar dia del pedimento
                        round=False,
                    )

                product.standard_price = price

    @api.depends('main_supplier_id', 'main_supplier_id.price', 'last_supplier_id', 'last_supplier_id.price')
    def _compute_accounting_standard_price(self):
        """
        Computes the product template standard cost based on completed and received purchase orders.
        Considers quantities, unit prices, and landed costs. Uses today's date for currency conversion if no landed cost is assigned per line.
        Used for accounting purposes, given that we need to rotate the last price on the original 'standard_price' field to populate the unit value of the
        valuation layers we decided to have a new dedicated field for soting the cost used on accounting. This coust is the historical average of ALL the purchases.

        WARNING; THE AVERAGE IS BASED ON THE WHOLE HISTORICAL RECORD OF PURHCASES, only distiguishes done and confirmed purchases.

        Args:
            landed_date: The date of the stock.landed.cost record related to the purchase.order.line
        Returns:
            None
            """

        for product in self:
            # Fetch all purchase order lines related to the product that are in completed and received orders
            order_lines = self.env['purchase.order.line'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('order_id.state', 'in', ['purchase', 'done']),  # Only consider completed orders
                ('order_id.picking_ids.state', '=', 'done'),  # Only consider orders with received pickings
            ])
            total_price = 0.0
            total_quantity = 0.0
            for line in order_lines:
                price = line.price_unit
                quantity = line.product_qty
                # Subtract returned quantities
                returned_quantity = sum(move.product_uom_qty for move in line.move_ids if move.state == 'done' and move.to_refund)
                net_quantity = quantity - returned_quantity
                if net_quantity <= 0:
                    continue
                landed_cost_date = line.landed_cost.date if line.landed_cost else fields.Date.context_today(self)
                currency_id = line.currency_id
                if currency_id.id != product.cost_currency_id.id:
                    price = currency_id._convert(
                        price,
                        product.cost_currency_id,
                        self.env.company,
                        landed_cost_date,  # Use the landed cost date or today if not available
                        round=False,
                    )
                total_price += price * net_quantity
                total_quantity += net_quantity
            if total_quantity > 0:
                avg = total_price / total_quantity
                product.accounting_standard_price = avg
            else:
                # If no historical records, fall back to main or last supplier pricing, this will use the fixed price on the supplier record
                # and convert the currency for today
                if product.main_supplier_id:
                    price = product.main_supplier_id.price
                    main_supplier_currency_id = product.main_supplier_id.currency_id
                    if main_supplier_currency_id.id != product.cost_currency_id.id:
                        price = main_supplier_currency_id._convert(
                            price,
                            product.cost_currency_id,
                            self.env.company,
                            fields.Date.context_today(self),
                            round=False,
                        )
                    product.accounting_standard_price = price
                    return
                if product.last_supplier_id:
                    price = product.last_supplier_id.price
                    last_supplier_currency_id = product.last_supplier_id.currency_id
                    if last_supplier_currency_id.id != product.cost_currency_id.id:
                        price = last_supplier_currency_id._convert(
                            price,
                            product.cost_currency_id,
                            self.env.company,
                            fields.Date.context_today(self),
                            round=False,
                        )
                    product.accounting_standard_price = price
