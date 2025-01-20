import logging
from odoo.tools import groupby
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    landed_cost_number = fields.Char(string="Pedimento", compute="_compute_landed_cost_number", store=False)
    is_multi_landed_cost = fields.Boolean(
        default=False,
        string="Tiene varios pedimentos",
        help="""
            Esta opción habilitará el uso de varios pedimentos en esta orden.
            El usuario deberá entonces hacerse responsable de:
                1. Asignar manualmente los pedimentos a cada línea.
                2. Asignar manualmente los traslados al pedimento usando el botón "ver costos destino" en el documento de traslado.
           """)
    # REFACTOR IDEA: Cada pedimento agregado genera un documento de traslado nuevo (No implementar hasta que se confirme).
    stock_landed_cost_ids = fields.Many2many("stock.landed.cost", string="Landed Costs")

    # === overwritten === #
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            order._update_landed_in_lines()
            order._update_landed_pickings()
            return True

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        self._update_landed_in_lines()
        return res

    @api.depends("stock_landed_cost_ids")
    def _compute_landed_cost_number(self):
        """
            Computes the local landed_cost_number field if only 1 record of 'landed.cost' is linked to the 'purchase.order', otherwise leave empty.
        """
        for order in self:
            if len(order.stock_landed_cost_ids) > 0:
                order.landed_cost_number = order.stock_landed_cost_ids[
                    0
                ].l10n_mx_edi_customs_number
            else:
                order.landed_cost_number = ""

    @api.model
    def _update_landed_in_lines(self):
        """
            Link the 'landed.cost' (if only 1 linked to the 'purchase.order') to each order_line.
        """
        for order in self:
            if order.is_multi_landed_cost:
                return
            for line in order.order_line:
                if len(order.stock_landed_cost_ids) > 0:
                    line.landed_cost = order.stock_landed_cost_ids[0]
                else:
                    line.landed_cost = False

    @api.model
    def _update_landed_pickings(self):
        """
            Updates the landed costs related to the 'purchase.order' related 'stock.piciking' records.

            If only 1 landed.cost:
            - Searches for valid 'stock.pickings'.
            - Links 'stock.pickings' to the 'landed.cost'.
            - If the 'landed.cost' is still in draft, validates it.
        """
        for order in self:
            if order.is_multi_landed_cost:
                return
            for line in order.order_line:
                pickings = line.order_id.picking_ids.filtered(lambda x:
                                                              x.state not in ("done", "cancel") and x.location_dest_id.usage in ("internal", "transit", "customer"))
                if pickings and len(pickings) > 0:
                    existing_picking_ids = (
                        line.landed_cost.picking_ids.ids
                        if line.landed_cost.picking_ids
                        else []
                    )

                    for picking in pickings:
                        line.landed_cost.write({
                            "picking_ids": [(6, 0, existing_picking_ids + [picking.id])],  # 6: Replace the list of IDs
                        })
                        if line.landed_cost.state == 'draft':
                            line.landed_cost.button_validate()

    def action_create_invoice(self):
        """
        Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            invoice_vals = order._prepare_invoice()
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({'sequence': sequence})
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({'sequence': sequence})
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list
        logger.warning("== == == ==")
        for invoice_val in invoice_vals_list:
            for line in invoice_val['invoice_line_ids']:
                logger.warning(line)
        logger.warning("== == == ==")
        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_move_type()

        return self.action_view_invoice(moves)
