from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    def _create_notice(self):
        
        _logger.warning('Entramos a metodo de crear aviso')
        
        
        