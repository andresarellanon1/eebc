from datetime import date
from odoo import api, models, _
from odoo.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # === overwritten === #
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            order._update_supplier_last_price()
        return res

    # === Handlers === #
    def _update_supplier_last_price(self):
        """
        Update the last price and related details of suppliers for the products in the purchase order lines.
        This method iterates through each order in the recordset and updates the supplier information
        based on the product and partner details. It performs the following actions:
        - Searches for the supplier information record matching the order partner.
        - Updates the supplier's last price with the unit price from the order line.
        - Always updates the supplier's currency to match the order currency.
        - Optionally updates the supplier's price unit if the `allow_price_recompute` flag is set.
        - Recomputes the product template's list price.
        - Recomputes the product template's standard price using the order date for currency conversion, which can be
          the landed cost date if present.
        - Creates a history record in `product.supplierinfo_history` with the updated pricing and order details.
        If the supplier's currency is updated but the `allow_price_recompute` flag is not set, and a
        currency mismatch occurs, an error is raised to prompt the user to activate the flag to avoid
        discrepancies in price and currency.
        Raises:
            ValidationError: If the supplier's currency is updated but the `allow_price_recompute` flag is not set
                             and a currency mismatch occurs.
        """
        for order in self:
            for line in order.order_line:
                for supplier in line.product_id.seller_ids:
                    # Search the supplierinfo record for the order partner
                    partner = line.order_id.partner_id if not line.order_id.partner_id.parent_id else line.order_id.partner_id.parent_id
                    if supplier.partner_id.id == partner.id:
                        supplier.last_price = line.price_unit  # Updates last_price
                        if supplier.currency_id.id != order.currency_id.id:  # Check for currency mismatch
                            # Raise an error if allow_price_recompute is not set
                            if not supplier.allow_price_recompute:
                                raise ValidationError(
                                    _("The supplier's currency has been updated but the 'Allow Price Recompute' flag is not set. "
                                      "Please activate the 'Allow Price Recompute' flag to avoid discrepancies in the price and currency.")
                                )
                            else:
                                supplier.currency_id = order.currency_id  # Update the currency to the latest used currency
                        # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                        if supplier.allow_price_recompute:
                            if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                                default_uom = line.product_id.product_tmpl_id.uom_po_id
                                supplier.price = line.product_uom._compute_price(line.price_unit, default_uom)
                            else:
                                supplier.price = line.price_unit

                        # Computes the list price of the product after updating prices of the supplier.
                        # If allow price recompute is active, at this point the product list price will be updated to the latest currency-price_unit of the supplier.
                        # line.product_id.product_tmpl_id._compute_list_price()
                        # conversion_date = line.date_approve or date.today()
                        # if line.landed_cost:
                        #     conversion_date = line.landed_cost.date
                        # supplier.conversion_date = conversion_date
                        # line.product_id.product_tmpl_id._compute_standard_price()
                        # Compute the global averange price. Used for defaulting accounting costs.
                        # line.product_id.product_tmpl_id._compute_accounting_standard_price()

                        self.env['product.supplierinfo_history'].create({
                            'datetime': line.order_id.write_date,
                            'price_unit': line.price_unit,
                            'order_id': line.order_id.id,
                            'product_template_id': line.product_id.product_tmpl_id.id,
                            'product_id': line.product_id.id,
                            'product_supplierinfo_id': supplier.id,
                            'landed_cost': line.landed_cost.id,
                            'currency_id': order.currency_id.id
                        })

    def _add_supplier_to_product(self):
        """
            Add the partner in the supplier list of the product if the supplier is not registered for
            this product. We limit to 10 the number of suppliers for a product to avoid the mess that
            could be caused for some generic products ("Miscellaneous").
        """
        for order in self:
            for line in order.order_line:
                # Do not add a contact as a supplier, always look for the parent company
                partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
                already_seller = (partner | self.partner_id) & line.product_id.seller_ids.mapped('partner_id')
                if line.product_id and not already_seller and len(line.product_id.seller_ids) <= 10:
                    # Convert the price in the right currency.
                    currency = partner.property_purchase_currency_id or self.env.company.currency_id
                    # Leave the price_unit and currency of the order
                    price = line.price_unit
                    # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                    if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                        default_uom = line.product_id.product_tmpl_id.uom_po_id
                        price = line.product_uom._compute_price(price, default_uom)
                    supplierinfo = self._prepare_supplier_info(partner, line, price, currency)
                    # In case the order partner is a contact address, a new supplierinfo is created on
                    # the parent company. In this case, we keep the product name and code.
                    seller = line.product_id._select_seller(
                        partner_id=line.partner_id,
                        quantity=line.product_qty,
                        date=line.order_id.date_order and line.order_id.date_order.date(),
                        uom_id=line.product_uom)
                    if seller:
                        supplierinfo['product_name'] = seller.product_name
                        supplierinfo['product_code'] = seller.product_code
                    vals = {'seller_ids': [(0, 0, supplierinfo)], }
                    # supplier info should be added regardless of the user access rights
                    line.product_id.product_tmpl_id.sudo().write(vals)
