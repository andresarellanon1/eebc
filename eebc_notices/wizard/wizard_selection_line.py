from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'
    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard')
    wizard_crud_id = fields.Many2one('notice.file.wizard', string='Wizard')

    notice_id = fields.Many2one('notices.notices', string='Avisos')
    quantity = fields.Float(string='Cantidad asignada', default=0, required=True)
    quantity_available = fields.Float(string='Cantidad disponible')

    in_or_out = fields.Boolean(
        string='Entrada o Salida',
        compute='_compute_value_text_in_or_out'
    )

    
    
   
    

    value_text_in_or_out = fields.Char(
        string='valor',
    )

    
    test_name = fields.Char(
        string='Nombre',
    )
    
  
    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning(vals_list)
        
        wizards = super(WizardSelectionLine, self).create(vals_list)
        for wizard in wizards:
            wizard.value_text_in_or_out = vals_list['value_text_in_or_out']
        return wizards

    @api.depends('value_text_in_or_out')
    def _compute_value_text_in_or_out(self):
        _logger.warning('entramos _compute_value_text_in_or_out')
        for record in self:
            _logger.warning('valor de texto in or out: %s', record.value_text_in_or_out)

            if record.value_text_in_or_out == 'in':
                _logger.warning('Se cumple')


                record.in_or_out = True
    
    