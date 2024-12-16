from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class WizardSelectionLotLine(models.TransientModel):
    _name = 'wizard.selection.lot.line'
    _description = 'Wizard Selection Lot Line'

    line_id = fields.Many2one('wizard.selection.line', string='Línea del Wizard', required=True)
    lot_id = fields.Many2one('stock.lot', string='Lote', required=True, )
    quantity = fields.Float(string='Cantidad', required=True)
