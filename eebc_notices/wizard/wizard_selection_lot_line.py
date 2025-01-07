from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class WizardSelectionLotLine(models.TransientModel):
    _name = 'wizard.selection.lot.line'
    _description = 'Wizard Selection Lot Line'

    line_id = fields.Many2one('wizard.selection.line', string='Línea del Wizard')
    lot_id = fields.Many2one('stock.lot', string='Lote')
    quantity = fields.Float(string='Cantidad')
    lot_quantity_available = fields.Float(string='Cantidad de lote disponible')
    

    @api.onchange('lot_quantity_available')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('La cantidad no puede ser negativa.')
            elif record.quantity > record.lot_quantity_available:
                raise ValidationError('No puede establecer una cantidad mayor a la disponible en el lote.')
