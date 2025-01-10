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
    'wizard.selection.lot.line', 'line_id', string='Lotes Asignados', 
        )
        

    
    quantity = fields.Float(string='Cantidad establecida', default=0, required=True)
    quantity_available = fields.Float(string='Cantidad disponible')
    quantity_available_lot = fields.Float(string='Cantidad disponible en lotes')

    #quantity_by_lot = fields.Float(string='Cantidad establecida de lotes', 
     #   compute='_compute_quantity_by_lot' )
    
   #@api.depends('lot_line_ids')
   # def _compute_quantity_by_lot(self):
    #    total = 0
     #   for lot in self.lot_line_ids:
      #      total += lot.quantity
        
       # self.quantity_by_lot = total

        #self.quantity_available
    ###
    


    in_or_out = fields.Boolean(
        string='Entrada o Salida',
    )


    
    aviso_name = fields.Char(
        string='Nombre',
        
    )

    @api.onchange('lot_line_ids')
    def _check_selected(self):
        for record in self:
            if record.lot_line_ids.is_selected:
                record.quantity_available_lot += 1

                
           

    @api.onchange('quantity')
    def _check_quantity_non_negative(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('La cantidad no puede ser negativa.')
