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
        self.split_stock_move(stock_move, self.split_quantity)

    def split_stock_move(self, original_move, split_quantity):
        # Verificar que la cantidad original sea válida
        if original_move.product_uom_qty <= 0:
            raise UserError("La cantidad original debe ser mayor que 0.")
        
        # Verificar que la cantidad de división sea válida
        if split_quantity <= 0 or split_quantity > original_move.product_uom_qty:
            raise UserError("La cantidad por línea debe ser mayor que 0 y menor o igual a la cantidad original.")
        
        # Calcular las cantidades divididas
        total_quantity = original_move.product_uom_qty
        split_quantities = []
        while total_quantity > 0:
            quantity = min(split_quantity, total_quantity)
            split_quantities.append(quantity)
            total_quantity -= quantity
        
        # Crear nuevos movimientos con las cantidades divididas
        for qty in split_quantities:
            new_move = original_move.copy(default={
                'product_uom_qty': qty,
                'move_orig_ids': [(6, 0, [original_move.id])],
            })
            new_move._action_confirm()
        
       