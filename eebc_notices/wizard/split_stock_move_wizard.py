from odoo import models, fields, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class SplitStockMoveWizard(models.TransientModel):
    _name = 'split.stock.move.wizard'
    _description = 'Wizard para dividir líneas de stock.move'

    stock_move_id = fields.Many2one('stock.move', string='Movimiento de Stock', required=True)
    split_quantity = fields.Float(string='Cantidad por Línea', required=True)

    def action_split_stock_move(self):
        self.ensure_one()
        stock_move = self.stock_move_id
        # Validaciones
        if self.split_quantity <= 0:
            raise UserError("La cantidad debe ser mayor que 0.")
        if self.split_quantity > stock_move.product_uom_qty:
            raise UserError("La cantidad no puede ser mayor que la cantidad original.")

        # Crear nuevas líneas de stock.move
        new_moves = self.env['stock.move']
        remaining_qty = stock_move.product_uom_qty
        new_move_vals = {}
        while remaining_qty > 0:
            qty = min(self.split_quantity, remaining_qty)
            # Crear un nuevo movimiento con los valores del original
            new_move_vals = {
                'product_uom_qty': qty,
                'product_uom': stock_move.product_uom.id,
                'product_id': stock_move.product_id.id,
                'location_id': stock_move.location_id.id,
                'location_dest_id': stock_move.location_dest_id.id,
                'picking_id': stock_move.picking_id.id,
                'name': stock_move.name,
                'origin': stock_move.origin,
                'state': 'draft',  # Estado inicial del nuevo movimiento
                'company_id': stock_move.company_id.id,
                'date': stock_move.date,
                'date_deadline': stock_move.date_deadline,
                'procure_method': stock_move.procure_method,
                'scrapped': stock_move.scrapped,
                'rule_id': stock_move.rule_id.id,
                # Agrega otros campos necesarios aquí
            }
            # new_move = self.env['stock.move'].create(new_move_vals)
            # new_moves += new_move
            _logger.warning('valor del diccionario 1: %s', new_move_vals)

            if stock_move.picking_id:
            
                stock_move.picking_id.write({
                    'move_ids_without_package': [(0,0, new_move_vals)]  # Agrega cada nuevo movimiento al campo one2many
                })
            remaining_qty -= qty
        _logger.warning('valor del diccionario 2: %s', new_move_vals)
        # Desactivar o cancelar la línea original
        stock_move.write({'product_uom_qty': 0, 'state': 'cancel'})

        # if stock_move.picking_id:
        
        #     stock_move.picking_id.write({
        #         'move_ids_without_package': [(0,0, new_move_vals)]  # Agrega cada nuevo movimiento al campo one2many
        #     })

        # Abrir la vista de los nuevos movimientos creados
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', new_moves.ids)],
            'target': 'current',
        }

