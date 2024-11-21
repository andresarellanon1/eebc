# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError



import logging

_logger = logging.getLogger(__name__)

class SelectNoticeWizard(models.TransientModel):
    _name = "select.notice.wizard"
    _description = "Wizard where we will select the notice to take the product"

    quantity = fields.Float(string="Demanda total", readonly=True,)
    line_ids = fields.One2many('wizard.selection.line', 'wizard_id', string='Lines', compute='_compute_line_ids')
    stock_move_id = fields.Many2one('stock.move', string='Traslado', domain=lambda self: self._get_stock_move_domain())

    # def _compute_stock_move_id(self):
    #     for record in self:
    #         record.stock_move_id = self.env['stock.move'].browse(self._context.get('active_id'))

    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'stock_move_id' in self._context:
            res['stock_move_id'] = self._context['stock_move_id']
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
        # Asignar el mensaje de error desde el contexto
        _logger.warning('VALOR DE RES1: %s', res)
        return res
    
    def _get_stock_move_domain(self):
        if not self:
            return []
        return [
            ('product_id', '=', self.stock_move_id.product_id.id),
            ('location_id', '=', self.stock_move_id.location_id.id),
            ('quantity', '>', 0)
        ]

    @api.depends('stock_move_id')
    def _compute_line_ids(self):
        for wizard in self:
            if not wizard.stock_move_id:
                continue  # No asignar nada si no hay stock_move_id

            notice_history_ids = self.env['notices.history'].search([
                ('quantity', '>', 0),
                ('product_id', '=', wizard.stock_move_id.product_id.id),
                ('location_id', '=', wizard.stock_move_id.location_id.id)
            ])
            _logger.warning('lineas de historial de aviso: %s',notice_history_ids )
            notice_ids = self.env['notices.notices'].search([('history_ids', 'in', notice_history_ids.ids)])
            _logger.warning('lineas de aviso: %s',notice_ids )

            # Limpiar las líneas existentes en caso de que haya alguna
            wizard.line_ids = [(5, 0, 0)]  # Eliminar líneas previas si existían

            # Crear las nuevas líneas en memoria
            lines = []
            for notice_history in notice_history_ids:
                for notice in notice_ids:
                    lines.append((0, 0, {
                        'notice_history_ids': [(0, 0, notice_history.id)],
                        'notice_ids': [(0, 0, notice.id)],
                        'quantity': 0  # Inicialmente 0, puedes cambiarlo si es necesario.
                    }))
            
            # Asignar las líneas al campo One2many
            wizard.line_ids = lines
            
            _logger.warning('lineas de wizard: %s',wizard.line_ids )
            

    def action_get_products(self):
        for wizard in self:
            total = 0
            for line in wizard.line_ids:
                total += line.quantity
            if total != wizard.quantity:
                raise ValidationError(f"La cantidad y la demanda deben coincidir. Total: {total} / Demanda: {wizard.quantity}")

            for line in wizard.line_ids:
                for notice in line.notice_ids:
                    notice.write({
                        'history_ids': [(0, 0, {
                            'location_id': wizard.stock_move_id.picking_id.location_id.id,
                            'location_dest_id': wizard.stock_move_id.picking_id.location_dest_id.id,
                            'quantity': line.quantity * (-1),
                            'picking_code': wizard.stock_move_id.picking_id.picking_type_code,
                            'origin': wizard.stock_move_id.picking_id.sale_id.name,
                            'sale_order_id': wizard.stock_move_id.picking_id.sale_id.id
                        })]
                    })

        return {'type': 'ir.actions.act_window_close'}



    
   
   