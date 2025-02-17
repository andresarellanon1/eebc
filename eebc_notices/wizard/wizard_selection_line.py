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


    
    lot_line_ids = fields.One2many(
    'wizard.selection.lot.line', 'line_id', string='Series/Lotes', 
        )
        


    quantity = fields.Float(string='Cantidad establecida', default=0, required=True)
    series_batch_quantity = fields.Float(string='Cantidad establecida en serie/lotes', default=0)

    quantity_available = fields.Float(string='Cantidad disponible')




    in_or_out = fields.Boolean(
        string='Entrada o Salida',
    )


    
    aviso_name = fields.Char(
        string='Nombre',
        
    )



    @api.onchange('lot_line_ids')
    def _check_selected(self):
        for record in self.lot_line_ids:
            if record.is_selected and not record.was_selected:
            # Marcar: Incrementar el contador
                self.series_batch_quantity += 1
                record.was_selected = True  # Actualizar el estado previo
            elif not record.is_selected and record.was_selected:
                # Desmarcar: Decrementar el contador
                self.series_batch_quantity -= 1
                record.was_selected = False  # Actualizar el estado previo


                
           

    @api.onchange('quantity')
    def _check_quantity_non_negative(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('La cantidad no puede ser negativa.')
