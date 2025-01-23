import logging
from odoo import api, fields, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    origin_sale_ids = fields.Many2many('sale.order',
                                       store=True,
                                       readonly=False,
                                       string='Sale Orders',
                                       compute="_compute_origin_sale_ids",
                                       help="")
    picking_ids = fields.Many2many('stock.picking', store=True)
    picking_date_done = fields.Datetime(string="Fecha entregado", compute="_compute_picking_date", store=True)

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
                except Exception:
                    move.origin_sale_ids = [(5, 0, 0)]

    @api.depends('picking_ids.state', 'picking_ids.date_done')
    def _compute_picking_date(self):
        for order in self:
            done_pickings = order.picking_ids.filtered(lambda p: p.state == 'done')
            if done_pickings:
                order.picking_date_done = done_pickings[0].date_done
            else:
                order.picking_date_done = False
