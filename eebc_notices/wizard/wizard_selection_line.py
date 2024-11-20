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
        location_id = self.wizard_id.stock_picking_location_id
        
        # current_wizard = self.env['select.notice.wizard'].browse()
        
        # current_wizard2 = self.env.context.get('active_id')
        
        # _logger.warning('current_wizard2: %s', current_wizard2)
        # _logger.warning('Location ID desde el dominio: %s', location_id)
        # _logger.warning('wizard_id: %s', current_wizard)
        # _logger.warning('Location ID desde el dominio: %s', location_id)
        domain = [('quantity', '>', 0)]
        if location_id:
            _logger.warning('valor del location id: %s', location_id)
            domain.append(('stock_location_origin_id', '=', self.wizard_id.stock_picking_location_id))
        return domain
