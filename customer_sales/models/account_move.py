from odoo.tools import float_is_zero
import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    material_change = fields.Boolean(default=False, string="Cambio de material")
    pre_invoice = fields.Boolean(
        default=False,
        string="Pre-factura",
        help="Siempre que se active este campo boleano, ademas de marcar la factura como pre-factura; causara que los costos se vuelvan zero en cada partida . Desactivarla re-computara los costos en base a las lineas de orden de venta correspondientes a cada partida.")
    is_government = fields.Boolean(string="Es del gobierno", compute="_compute_is_government", store=True)
    customer_reference = fields.Char(string="Orden de compra", help="Referencia de la orden de compra del cliente. Este campo no representa una orden de compra dentro de odoo. Se refiere a una orden de compra en el sistema del cliente.")
    sale_cost = fields.Float('Costo total', compute="_compute_sale_cost", store=False)
    origin_purchase_ids = fields.Many2many('purchase.order',
                                           store=True,
                                           readonly=False,
                                           string='Purchase Orders',
                                           compute="_compute_origin_purchase_ids",
                                           help="")

    origin_sale_ids = fields.Many2many('sale.order',
                                       store=True,
                                       readonly=False,
                                       string='Sale Orders',
                                       compute="_compute_origin_sale_ids",
                                       help="")

    picking_ids = fields.Many2many('stock.picking',
                                   store=True
                                   )
    picking_date_done = fields.Datetime(string="Fecha entregado", compute="_compute_picking_date", store=True)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.onchange_pre_invoice_toggle()
        return res

    @api.depends('partner_id')
    def _compute_is_government(self):
        for move in self:
            move.is_government = move.partner_id.is_government if move.partner_id else False

    @api.onchange('pre_invoice', 'is_government', 'material_change')
    def onchange_pre_invoice_toggle(self):
        for move in self:
            logger.warning(move.name)
            for line in move.invoice_line_ids:
                line._compute_sale_unit_cost()

    @api.depends('invoice_line_ids', 'pre_invoice', 'is_government', 'material_change')
    def _compute_sale_cost(self):
        for move in self:
            cost = 0.00
            for line in move.invoice_line_ids:
                cost += line.sale_unit_cost * line.quantity

            move.sale_cost = cost

    @api.depends('line_ids')
    def _compute_origin_purchase_ids(self):
        for move in self:
            purchase_ids = {line.purchase_line_id.order_id.id for line in move.line_ids if line.purchase_line_id}
            if purchase_ids:
                origins = self.env['purchase.order'].browse(purchase_ids)
                move.origin_purchase_ids = [(6, 0, origins.ids)]
            else:
                # logger.warning('No purchase orders found, cannot set origin_purchase_ids')
                move.origin_purchase_ids = [(5, 0, 0)]

    def compute_origin_sale_all(self):
        moves = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        for move in moves:
            move._compute_origin_sale_ids()

    def compute_sale_unit_cost_all(self):
        moves = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        for move in moves:
            for line in move.invoice_line_ids:
                line._compute_sale_unit_cost()

    @api.depends('line_ids')
    def _compute_origin_sale_ids(self):
        for move in self:
            sale_ids = {line.sale_line_ids.order_id.id for line in move.line_ids if line.sale_line_ids}
            if sale_ids:
                origins = self.env['sale.order'].browse(sale_ids)
                move.origin_sale_ids = [(6, 0, origins.ids)]
            else:
                try:
                    domain = [('state', '=', 'cancel')]
                    move_ids = self.env['account.move'].search(domain)
                    reinvoice_id = move_ids.filtered(lambda record: record.l10n_mx_edi_cfdi_cancel_id.id == move.id)
                    if reinvoice_id:
                        # TODO: sort by date to always get the oldest canceled account.move
                        sale_ids = {line.sale_line_ids.order_id.id for line in reinvoice_id[:1].line_ids if line.sale_line_ids}
                        origins = self.env['sale.order'].browse(sale_ids)
                        move.origin_sale_ids = [(6, 0, origins.ids)]
                    else:
                        move.origin_sale_ids = [(5, 0, 0)]
                except Exception as e:
                    move.origin_sale_ids = [(5, 0, 0)]

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.move_type in ['out_invoice', 'out_refund']:
            return 'morvil_report_invoice.morvil_out_invoice_template'
        else:
            return 'account.report_invoice_document'

    @api.depends('picking_ids.state', 'picking_ids.date_done')
    def _compute_picking_date(self):
        for order in self:
            done_pickings = order.picking_ids.filtered(lambda p: p.state == 'done')
            if done_pickings:
                order.picking_date_done = done_pickings[0].date_done
            else:
                order.picking_date_done = False

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        moves._check_and_update_partner_credit()
        for move in moves:
            line_order_references = set()  # Use a set to avoid duplicates
            for line in move.line_ids:
                source_order_customer_reference = line.sale_line_ids.order_id.customer_reference
                if source_order_customer_reference:
                    line_order_references.add(source_order_customer_reference)  # Add to the set

            move.customer_reference = ','.join(line_order_references)
        return moves

    @api.onchange("partner_id")
    def _onchange_partner_set_addresses_default(self):
        for move in self:
            move.partner_shipping_id = move.partner_id

    def _check_and_update_partner_credit(self):
        for move in self:
            partner = move.partner_id
            partner._check_credit_limit(move.amount_residual)
            if partner.customer_credit_suspend:
                logger.warning(f'Credito suspendido para el cliente {partner.name}')
    #
    # def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
    #     ''' Prepare values used to create the journal items (account.move.line) corresponding to the Cost of Good Sold
    #     lines (COGS) for customer invoices.
    #
    #     Example:
    #
    #     Buy a product having a cost of 9 being a storable product and having a perpetual valuation in FIFO.
    #     Sell this product at a price of 10. The customer invoice's journal entries looks like:
    #
    #     Account                                     | Debit | Credit
    #     ---------------------------------------------------------------
    #     200000 Product Sales                        |       | 10.0
    #     ---------------------------------------------------------------
    #     101200 Account Receivable                   | 10.0  |
    #     ---------------------------------------------------------------
    #
    #     This method computes values used to make two additional journal items:
    #
    #     ---------------------------------------------------------------
    #     220000 Expenses                             | 9.0   |
    #     ---------------------------------------------------------------
    #     101130 Stock Interim Account (Delivered)    |       | 9.0
    #     ---------------------------------------------------------------
    #
    #     Note: COGS are only generated for customer invoices except refund made to cancel an invoice.
    #
    #     :return: A list of Python dictionary to be passed to env['account.move.line'].create.
    #     '''
    #     lines_vals_list = []
    #     price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
    #     for move in self:
    #         # Make the loop multi-company safe when accessing models like product.product
    #         move = move.with_company(move.company_id)
    #
    #         if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
    #             continue
    #
    #         for line in move.invoice_line_ids:
    #
    #             # Filter out lines being not eligible for COGS.
    #             if not line._eligible_for_cogs():
    #                 continue
    #
    #             # Retrieve accounts needed to generate the COGS.
    #             accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
    #             debit_interim_account = accounts['stock_output']
    #             credit_expense_account = accounts['expense'] or move.journal_id.default_account_id
    #             if not debit_interim_account or not credit_expense_account:
    #                 continue
    #
    #             # Compute accounting fields.
    #             sign = -1 if move.move_type == 'out_refund' else 1
    #             price_unit = line._stock_account_get_anglo_saxon_price_unit()
    #             amount_currency = sign * line.quantity * price_unit
    #
    #             logger.warning(f"[ {line.name} ] ACCOUNT MOVE CREATING COGS [ {sign} * {line.quantity}  * {price_unit}  = {amount_currency}]")
    #
    #             if move.currency_id.is_zero(amount_currency) or float_is_zero(price_unit, precision_digits=price_unit_prec):
    #                 continue
    #
    #             # Add interim account line.
    #             lines_vals_list.append({
    #                 'name': line.name[:64],
    #                 'move_id': move.id,
    #                 'partner_id': move.commercial_partner_id.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'quantity': line.quantity,
    #                 'price_unit': price_unit,
    #                 'amount_currency': -amount_currency,
    #                 'account_id': debit_interim_account.id,
    #                 'display_type': 'cogs',
    #                 'tax_ids': [],
    #                 'cogs_origin_id': line.id,
    #             })
    #
    #             # Add expense account line.
    #             lines_vals_list.append({
    #                 'name': line.name[:64],
    #                 'move_id': move.id,
    #                 'partner_id': move.commercial_partner_id.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_id': line.product_uom_id.id,
    #                 'quantity': line.quantity,
    #                 'price_unit': -price_unit,
    #                 'amount_currency': amount_currency,
    #                 'account_id': credit_expense_account.id,
    #                 'analytic_distribution': line.analytic_distribution,
    #                 'display_type': 'cogs',
    #                 'tax_ids': [],
    #                 'cogs_origin_id': line.id,
    #             })
    #
    #     return lines_vals_list
    #
