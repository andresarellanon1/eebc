from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'
    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard')
    wizard_crud_id = fields.Many2one('notice.file.wizard', string='Wizard')

    notice_id = fields.Many2one('notices.notices', string='Avisos')



    # lot_line_ids = fields.One2many(
    # 'wizard.selection.lot.line', 'line_id', string='Lotes Asignados', 
    #     )

    
    quantity = fields.Float(string='Cantidad asignada', default=0, required=True)
    quantity_available = fields.Float(string='Cantidad disponible')

    in_or_out = fields.Boolean(
        string='Entrada o Salida',
    )


    
    aviso_name = fields.Char(
        string='Nombre',
        
    )


    @api.onchange('quantity')
    def _check_quantity_non_negative(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('La cantidad no puede ser negativa.')
