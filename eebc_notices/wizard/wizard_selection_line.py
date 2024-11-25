from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'
    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard')
    notice_id = fields.Many2one('notices.notices', string='Avisos', readonly=True )
    quantity = fields.Float(string='Cantidad asignada', default=0, required=True)
    quantity_available = fields.Float(
        string='Cantidad disponible',
        readonly=True,
        related='notice_id.quantity_to_show'
    )
   


  
    @api.model
    def default_get(self, fields):
        res = super(WizardSelectionLine, self).default_get(fields)
        if self.notice_id:
            self.quantity_available = self.notice_id.quantity
       
        _logger.warning('vALORDE LINEASS RES wwwwwwazaaaaaaaaaa : %s',res)
        
        return res
    