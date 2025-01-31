from odoo import models, fields, api

class SplitMoveLineWizard(models.TransientModel):
    _name = 'split.move.line.wizard'
    _description = 'Wizard para dividir líneas de stock.move.line'

    move_id = fields.Many2one('stock.move', string='Movimiento a Dividir', required=True)
    quantity = fields.Float(string='Cantidad a Dividir', required=True)

    def action_split(self):
        """
        Divide el stock.move en múltiples stock.move.line según la cantidad especificada.
        """
        self.move_id.split_move_lines(self.quantity)
        return {'type': 'ir.actions.act_window_close'}

    def action_merge(self):
        """
        Junta las líneas seleccionadas de stock.move.line en un solo stock.move.
        """
        lines_to_merge = self.env['stock.move.line'].browse(self._context.get('active_ids'))
        self.move_id.merge_move_lines(lines_to_merge)
        return {'type': 'ir.actions.act_window_close'}