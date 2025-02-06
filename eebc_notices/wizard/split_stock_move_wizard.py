from odoo import models, fields, api
from odoo.exceptions import UserError


class SplitStockMoveWizard(models.TransientModel):
    _name = 'split.stock.move.wizard'
    _description = 'Wizard para dividir líneas de stock.move'

    stock_move_id = fields.Many2one('stock.move', string='Movimiento de Stock', required=True)
    split_quantity = fields.Float(string='Cantidad por Línea', required=True)

    def action_split_stock_move(self):
        self.ensure_one()
        stock_move = self.stock_move_id
        if self.split_quantity <= 0:
            raise UserError("La cantidad debe ser mayor que 0.")
        if self.split_quantity > stock_move.product_uom_qty:
            raise UserError("La cantidad no puede ser mayor que la cantidad original.")

        # Crear nuevas líneas de stock.move
        new_moves = self.env['stock.move']
        remaining_qty = stock_move.product_uom_qty
        while remaining_qty > 0:
            qty = min(self.split_quantity, remaining_qty)
            new_move = stock_move.copy(default={'product_uom_qty': qty})
            new_moves += new_move
            remaining_qty -= qty

        # Desactivar la línea original
        stock_move.write({'product_uom_qty': 0, 'state': 'cancel'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', new_moves.ids)],
            'target': 'current',
        }