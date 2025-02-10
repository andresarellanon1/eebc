from odoo import models, fields, api
from odoo.exceptions import UserError


class SplitStockMoveWizard(models.TransientModel):
    _name = 'split.stock.move.wizard'
    _description = 'Wizard para dividir líneas de stock.move'

    stock_move_id = fields.Many2one('stock.move', string='Movimiento de Stock', required=True)
    split_quantity = fields.Float(string='Cantidad por Línea', required=True)
    new_move_lines = fields.One2many(
        'split.stock.move.wizard.line',  # Modelo relacionado
        'wizard_id',  # Campo Many2one en el modelo relacionado
        string='Líneas de Movimientos',
    )

    def action_split_stock_move(self):
        self.ensure_one()
        stock_move = self.stock_move_id

        # Validaciones
        if self.split_quantity <= 0:
            raise UserError("La cantidad debe ser mayor que 0.")
        if self.split_quantity > stock_move.product_uom_qty:
            raise UserError("La cantidad no puede ser mayor que la cantidad original.")

        # Limpiar líneas existentes
        self.new_move_lines.unlink()

        # Crear nuevas líneas de stock.move
        remaining_qty = stock_move.product_uom_qty
        while remaining_qty > 0:
            qty = min(self.split_quantity, remaining_qty)
            # Crear una nueva línea en el wizard
            self.env['split.stock.move.wizard.line'].create({
                'wizard_id': self.id,
                'product_id': stock_move.product_id.id,
                'product_uom_qty': qty,
                'location_id': stock_move.location_id.id,
                'location_dest_id': stock_move.location_dest_id.id,
                'name': stock_move.name,
            })
            remaining_qty -= qty

        # Abrir la vista del wizard para mostrar las líneas
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'split.stock.move.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_confirm(self):
        """Confirmar la creación de los nuevos movimientos."""
        self.ensure_one()
        stock_move = self.stock_move_id

        # Crear nuevos movimientos de inventario
        new_moves = self.env['stock.move']
        for line in self.new_move_lines:
            new_move_vals = {
                'product_uom_qty': line.product_uom_qty,
                'product_id': line.product_id.id,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'name': line.name,
                'origin': stock_move.origin,
                'state': 'draft',  # Estado inicial del nuevo movimiento
                'picking_id': stock_move.picking_id.id,
                'company_id': stock_move.company_id.id,
                'date': stock_move.date,
                'date_deadline': stock_move.date_deadline,
                # Agrega otros campos necesarios aquí
            }
            new_move = self.env['stock.move'].create(new_move_vals)
            new_moves += new_move

        # Desactivar o cancelar la línea original
        stock_move.write({'product_uom_qty': 0, 'state': 'cancel'})

        # Abrir la vista de los nuevos movimientos creados
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', new_moves.ids)],
            'target': 'current',
        }


class SplitStockMoveWizardLine(models.TransientModel):
    _name = 'split.stock.move.wizard.line'
    _description = 'Líneas del wizard para dividir movimientos de stock'

    wizard_id = fields.Many2one('split.stock.move.wizard', string='Wizard', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    product_uom_qty = fields.Float(string='Cantidad', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación de Origen', required=True)
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de Destino', required=True)
    name = fields.Char(string='Descripción')