from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'

    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard', required=True)
    record_id = fields.Many2one('notices.notices', string='Aviso', required=True, domain=lambda self: self._get_notice_domain())
    quantity = fields.Float(string='Quantity', default=1.0, required=True)



    def _get_notice_domain(self):
        """Get domain to filter notices based on cantidad"""
        _logger.warning('Contexto: %s',self._context['location_id'])
        return [('quantity', '>', 0),('stock_location_origin_id','=',self._context['location_id'])] if self.quantity else []