from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        _logger.warning('entramos a validate de picking')

        # Llama al método original para mantener su funcionalidad
        res = super(StockPicking, self).button_validate()


        # Iterar sobre los pickings validados
        for picking in self:
            # Obtener los `stock_move_id` de las líneas de `move_ids_without_package`
            move_ids =  picking.move_ids_without_package.ids
            
            # picking.move_ids_without_package.mapped('id')

            _logger.warning('move_ids: %s', move_ids)


            # Filtrar los historiales relacionados y actualizar su estado
            histories = self.env['notices.history'].search([('stock_move_id', 'in', move_ids)])

            _logger.warning('histories: %s', histories)

            histories.write({'state': 'approved'})  # Cambia a tu estado deseado

        return res

    def action_cancel(self):
        _logger.warning('entramos a cancel de picking')
        # Llama al método original para mantener su funcionalidad
        res = super(StockPicking, self).action_cancel()

        # Iterar sobre los pickings cancelados
        for picking in self:
            # Obtener los `stock_move_id` de las líneas de `move_ids_without_package`
            move_ids = picking.move_ids_without_package.mapped('id')

            # Filtrar los historiales relacionados y actualizar su estado
            histories = self.env['notices.history'].search([('stock_move_id', 'in', move_ids)])
            histories.write({'state': 'canceled'})  # Cambia los estados a 'canceled'

        return res

    def open_fragment_wizard(self):
        return {
            'name': "Fragmentar Línea de Movimiento",
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line.fragment.wizard',
            'view_mode': 'form',
            'target': 'new',
                'context': {'default_move_line_id': self.id}
            }
        
 