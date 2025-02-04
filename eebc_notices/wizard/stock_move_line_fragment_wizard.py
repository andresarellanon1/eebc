from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMoveLineFragmentWizard(models.TransientModel):
    _name = 'stock.move.line.fragment.wizard'
    _description = 'Fragmentar Línea de Movimiento de Inventario'

    move_line_id = fields.Many2one('stock.move.line', string="Línea de Movimiento", required=True)
    total_quantity = fields.Float(string="Cantidad Total", readonly=True)
    fragment_lines = fields.One2many(
        'stock.move.line.fragment.line', 
        'wizard_id', 
        string="Fragmentaciones"
    )


      
    @api.model
    def default_get(self, fields):
        res = super(StockMoveLineFragmentWizard, self).default_get(fields)
        if 'default_move_line_id' in self._context:
            stock_move_obj = self.env['stock.move'].search([('id','=',self._context['default_move_line_id'])])
            res['total_quantity'] = stock_move_obj.product_uom_qty
      
        return res

    @api.depends('fragment_lines.quantity')
    def _compute_total_fragment_quantity(self):
        for record in self:
            record.total_fragment_quantity = sum(record.fragment_lines.mapped('quantity'))

    total_fragment_quantity = fields.Float(
        string="Cantidad Fragmentada", 
        compute="_compute_total_fragment_quantity", 
        store=True
    )

    def action_confirm_fragmentation(self):
        """ Divide la línea de stock.move.line en múltiples líneas """
        self.ensure_one()
        total_new_qty = sum(self.fragment_lines.mapped('quantity'))

        if total_new_qty > self.total_quantity:
            raise ValidationError("La suma de las cantidades fragmentadas no puede ser mayor que la cantidad original.")

        move_line = self.move_line_id

        for fragment in self.fragment_lines:
            self.env['stock.move.line'].create({
                'move_id': move_line.move_id.id,
                'product_id': move_line.product_id.id,
                'quantity_product_uom': fragment.quantity,
                'location_id': move_line.location_id.id,
                'location_dest_id': move_line.location_dest_id.id,
                'lot_id': move_line.lot_id.id if move_line.lot_id else False,
                'package_id': move_line.package_id.id if move_line.package_id else False,
            })

        # Eliminar la línea original después de la fragmentación
        move_line.unlink()
        
        return {'type': 'ir.actions.act_window_close'}
