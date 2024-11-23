from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'
    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard')
    notice_id = fields.Many2one('notices.notices', string='Avisos', readonly=True )
    quantity = fields.Float(string='Cantidad asignada', default=0, required=True)
    quantity_available = fields.Float(string='Cantidad disponible',readonly=True, 
        compute='_compute_notice_id' )
    
    @api.depends('notice_id')
    def _compute_notice_id(self):
        for record in self:
            record.quantity_available = self.notice_id.quantity
    
    
    


  
    