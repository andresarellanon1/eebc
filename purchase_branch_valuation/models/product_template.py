from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import logging

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    #
    # accounting_standard_price = fields.Float(
    #     string="Costo contable",
    #     help='Se computa desde el historico de ventas. Ignora los proveedores, usa directamente todas las compras que contengan este producto.',
    #     compute="_compute_accounting_standard_price",
    #     digits="Product Price",
    #     store=True,
    #     readonly=True,
    # )
    #
    # # === overwritten === #
    #
    # @api.depends("seller_ids.is_main_supplier")
    # def _compute_main_supplier_id(self):
    #     super(ProductTemplate, self)._compute_main_supplier_id()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("main_supplier_id.price")
    # def _compute_main_supplier_last_price(self):
    #     super(ProductTemplate, self)._compute_main_supplier_last_price()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("main_supplier_id.currency_id")
    # def _compute_main_supplier_last_order_currency_id(self):
    #     super(ProductTemplate, self)._compute_main_supplier_last_order_currency_id()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("supplier_history")
    # def _compute_last_supplier_id(self):
    #     super(ProductTemplate, self)._compute_last_supplier_id()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("supplier_history")
    # def _compute_last_supplier_datetime(self):
    #     super(ProductTemplate, self)._compute_last_supplier_datetime()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("last_supplier_id.price")
    # def _compute_last_supplier_last_price(self):
    #     super(ProductTemplate, self)._compute_last_supplier_last_price()
    #     for template in self:
    #         template._compute_list_price()
    #
    # @api.depends("last_supplier_id.currency_id")
    # def _compute_last_supplier_last_order_currency_id(self):
    #     super(ProductTemplate, self)._compute_last_supplier_last_order_currency_id()
    #     for template in self:
    #         template._compute_list_price()
    #
    # # === Handlers === #
    #
    # def _compute_safe_margin_add(self):
    #     for product in self:
    #         supplier_currency = None
    #         added_value = 0.00
    #         safe_margin = self.env["ir.config_parameter"].sudo().get_param("sale.safe_margin")
    #         if product.main_supplier_id:
    #             supplier_currency = product.main_supplier_id.currency_id
    #             supplier_last_price = product.main_supplier_last_price
    #         elif product.last_supplier_id:
    #             supplier_currency = product.last_supplier_id.currency_id
    #             supplier_last_price = product.last_supplier_last_price
    #         if supplier_currency:
    #             if supplier_currency.id != self.env.company.currency_id.id:
    #                 added_value = supplier_last_price * float(safe_margin)
    #             else:
    #                 raise ValidationError(f"Proveedor sin divisa: {product.last_supplier_id}")
    #         return added_value
    #
    # def _compute_list_price(self):
    #     """
    #     Computes the product template list price based on the supplier's price (main supplier if available, otherwise last supplier).
    #     If necessary, converts the supplier's price from their currency to the product's cost currency.
    #     Applies a safe margin addition if the main supplier is used.
    #
    #     The process involves:
    #     1. Retrieving the price and currency of the relevant supplier.
    #     2. Converting the price to the product's cost currency if needed.
    #     3. Updating the product's list price.
    #
    #     If no suppliers are available, sets the list price to 0.00.
    #
    #     The objetive is to provide a default list_price based on the cost (and safe margin) so we can have it as an input to the advanced pricelists.
    #     """
    #
    #     def convert_currency(amount, from_currency, to_currency):
    #         return from_currency._convert(
    #             amount,
    #             to_currency,
    #             self.env.company,
    #             date.today(),
    #             round=False,
    #         )
    #     for product in self:
    #         if not product.main_supplier_id and not product.last_supplier_id:
    #             product.list_price = 0.00
    #             return
    #         supplier = product.main_supplier_id if product.main_supplier_id else product.last_supplier_id
    #         price = supplier.price
    #         currency_id = supplier.currency_id
    #         if price is not None:
    #             if currency_id.id != self.env.company.currency_id.id:
    #                 price = convert_currency(price, currency_id, self.env.company.currency_id)
    #             safe_added = self._compute_safe_margin_add()
    #             product.list_price = price + safe_added
    #
    # # @api.depends_context('company')
    # def _compute_standard_price(self):
    #     """
    #         overwritten, the original was:
    #             def _compute_standard_price(self):
    #                 # Depends on force_company context because standard_price is company_dependent
    #                 # on the product_product
    #                 self._compute_template_field_from_variant_field('standard_price')
    #
    #             def _compute_template_field_from_variant_field(self, fname, default=False):
    #                 Sets the value of the given field based on the template variant values
    #
    #                 Equals to product_variant_ids[fname] if it's a single variant product.
    #                 Otherwise, sets the value specified in ``default``.
    #                 It's used to compute fields like barcode, weight, volume..
    #
    #                 :param str fname: name of the field to compute
    #                     (field name must be identical between product.product & product.template models)
    #                 :param default: default value to set when there are multiple or no variants on the template
    #                 :return: None
    #
    #                 for template in self:
    #                     variant_count = len(template.product_variant_ids)
    #                     if variant_count == 1:
    #                         template[fname] = template.product_variant_ids[fname]
    #                     elif variant_count == 0 and self.env.context.get("active_test", True):
    #                         # If the product has no active variants, retry without the active_test
    #                         template_ctx = template.with_context(active_test=False)
    #                         template_ctx._compute_template_field_from_variant_field(fname, default=default)
    #                     else:
    #                         template[fname] = default
    #
    #             def _set_product_variant_field(self, fname):
    #                 Propagate the value of the given field from the templates to their unique variant.
    #
    #                 Only if it's a single variant product.
    #                 It's used to set fields like barcode, weight, volume..
    #
    #                 :param str fname: name of the field whose value should be propagated to the variant.
    #                     (field name must be identical between product.product & product.template models)
    #
    #                 for template in self:
    #                     count = len(template.product_variant_ids)
    #                     if count == 1:
    #                         template.product_variant_ids[fname] = template[fname]
    #                     elif count == 0:
    #                         archived_variants = self.with_context(active_test=False).product_variant_ids
    #                         if len(archived_variants) == 1:
    #                             archived_variants[fname] = template[fname]
    #
    #        WARNING:
    #        USED FOR STOCK VALUATION LAYERS WITH CUSTOMS LANDED DATE CONVERSION RATE.
    #        DO NOT USE THIS FIELD FOR ACCOUNTING ANYMORE.
    #
    #        Computes the product template standard cost given the supplier(main or last if not main selected) price and currency.
    #        Converts currency for the passed date and saves the last instance of the date for follow up calls.
    #        The date is only passed when called from a purhcase document confirmation action.
    #
    #        Args:
    #            landed_date: The date of the stock.landed.cost record related to the purhcase.order.line
    #     """
    #     for product in self:
    #         if (not product.main_supplier_id) and (not product.last_supplier_id):
    #             product.standard_price = 0.00
    #             return
    #         # Main supplier is selected #
    #         if product.main_supplier_id:
    #             price = product.main_supplier_id.price
    #             main_supplier_currency_id = product.main_supplier_id.currency_id
    #             if main_supplier_currency_id.id != product.cost_currency_id.id:
    #                 price = main_supplier_currency_id._convert(
    #                     price,
    #                     product.cost_currency_id,
    #                     self.env.company,
    #                     product.main_supplier_id.last_landed_date,  # Usar dia del pedimento, se usa `last_landed_date` en lugar de una landed_date especifica a la entrada actual porque el campo `standard_price` se 'rota' con cada entrada y/o campo de proveedor principal/ultimo.
    #                     round=False,
    #                 )
    #             product.standard_price = price
    #             return
    #         # Main supplier is NOT selected #
    #         if product.last_supplier_id:
    #             price = product.last_supplier_id.price
    #             last_supplier_currency_id = product.last_supplier_id.currency_id
    #             if last_supplier_currency_id.id != product.cost_currency_id.id:
    #                 price = last_supplier_currency_id._convert(
    #                     price,
    #                     product.cost_currency_id,
    #                     self.env.company,
    #                     product.last_supplier_id.last_landed_date,  # Usar dia del pedimento
    #                     round=False,
    #                 )
    #             product.standard_price = price
    #
    # @api.depends('main_supplier_id', 'main_supplier_id.price', 'last_supplier_id', 'last_supplier_id.price')
    # def _compute_accounting_standard_price(self):
    #     """
    #         Computes the product template standard cost based on completed and received purchase orders.
    #         Considers quantities, unit prices, and landed costs. Uses today's date for currency conversion if no landed cost is assigned per line.
    #         Used for accounting purposes. Given that we need to rotate the last price on the original 'standard_price' field to populate the unit price of the
    #         valuation layers; we decided to have a new dedicated field for storing the global average cost used.
    #         This cost is the historical average of ALL the purchases.
    #
    #         WARNING:
    #         THE AVERAGE IS BASED ON THE WHOLE HISTORICAL RECORD OF PURHCASES, only distiguishes done and confirmed purchases.
    #         TODO: add branch checking distinctions
    #     """
    #     for product in self:
    #         # Fetch all purchase order lines related to the product that are in completed and received orders
    #         order_lines = self.env['purchase.order.line'].search([
    #             ('product_id.product_tmpl_id', '=', product.id),
    #             ('order_id.state', 'in', ['purchase', 'done']),  # Only consider completed orders
    #             ('order_id.picking_ids.state', '=', 'done'),  # Only consider orders with received pickings
    #         ])
    #         total_price = 0.0
    #         total_quantity = 0.0
    #         for line in order_lines:
    #             price = line.price_unit
    #             quantity = line.product_qty
    #             # Subtract returned quantities
    #             returned_quantity = sum(move.product_uom_qty for move in line.move_ids if move.state == 'done' and move.to_refund)
    #             net_quantity = quantity - returned_quantity
    #             if net_quantity <= 0:
    #                 continue
    #             landed_cost_date = line.landed_cost.date if line.landed_cost else fields.Date.context_today(self)
    #             currency_id = line.currency_id
    #             if currency_id.id != product.cost_currency_id.id:
    #                 price = currency_id._convert(
    #                     price,
    #                     product.cost_currency_id,
    #                     self.env.company,
    #                     landed_cost_date,  # Use the landed cost date or today if not available
    #                     round=False,
    #                 )
    #             total_price += price * net_quantity
    #             total_quantity += net_quantity
    #         if total_quantity > 0:
    #             avg = total_price / total_quantity
    #             product.accounting_standard_price = avg
    #         else:
    #             # If no historical records, fall back to main or last supplier pricing, this will use the fixed price on the supplier record
    #             # and convert the currency for today
    #             if product.main_supplier_id:
    #                 price = product.main_supplier_id.price
    #                 main_supplier_currency_id = product.main_supplier_id.currency_id
    #
    #                 if main_supplier_currency_id.id != product.cost_currency_id.id:
    #                     price = main_supplier_currency_id._convert(
    #                         price,
    #                         product.cost_currency_id,
    #                         self.env.company,
    #                         fields.Date.context_today(self),
    #                         round=False,
    #                     )
    #                 product.accounting_standard_price = price
    #                 return
    #             if product.last_supplier_id:
    #                 price = product.last_supplier_id.price
    #                 last_supplier_currency_id = product.last_supplier_id.currency_id
    #
    #                 if last_supplier_currency_id.id != product.cost_currency_id.id:
    #                     price = last_supplier_currency_id._convert(
    #                         price,
    #                         product.cost_currency_id,
    #                         self.env.company,
    #                         fields.Date.context_today(self),
    #                         round=False,
    #                     )
    #                 product.accounting_standard_price = price
