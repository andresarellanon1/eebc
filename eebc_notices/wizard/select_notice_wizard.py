# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError



import logging

_logger = logging.getLogger(__name__)

class SelectNoticeWizard(models.TransientModel):
    _name = "select.notice.wizard"
    _description = "Wizard where we will select the notice to take the product"

    notice_ids = fields.Many2many(
        'notices.notices',
        string='Avisos',
    )
    quantity_ids = fields.One2many(
        'wizard.selection.line',
        'wizard_id',
        string='Cantidades',
    )
    quantity = fields.Float(string="Demanda total", readonly=True,)
    stock_move_id = fields.Many2one('stock.move', string='Traslado')

    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'stock_move_id' in self._context:
            res['stock_move_id'] = self._context['stock_move_id']
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
        if 'lines' in self._context:
            res['quantity_ids'] = self._context['lines']
        _logger.warning('vALORDE LINEASS RES : %s',res)
        
        return res
    

    def action_get_products(self):
        for wizard in self:
            _logger.warning('first for')

            total = 0
            for line in wizard.quantity_ids:
                _logger.warning('second for')

                total += line.quantity
            _logger.warning('Valor de total: %s', total)
            if total != wizard.quantity:
                raise ValidationError(f"La cantidad y la demanda deben coincidir. Total: {total} / Demanda: {wizard.quantity}")

            for line in wizard.quantity_ids:
                for notice in line.notice_id:
                    notice.sudo().write({
                        'history_ids': [(0, 0, {
                            'location_id': wizard.stock_move_id.picking_id.location_id.id,
                            'location_dest_id': wizard.stock_move_id.picking_id.location_dest_id.id,
                            'quantity': line.quantity * (-1),
                            'picking_code': wizard.stock_move_id.picking_id.picking_type_code,
                            'origin': wizard.stock_move_id.picking_id.sale_id.name,
                            'sale_order_id': wizard.stock_move_id.picking_id.sale_id.id,
                            'product_id': wizard.stock_move_id.product_id.id,
                            'folio': notice.folio,
                            'purchase_order_id':self._context['purchase_order_id']
                        })]
                    })

        return {'type': 'ir.actions.act_window_close'}



    
   
   