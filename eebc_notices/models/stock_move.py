from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    def create_notice(self):
        
        # notice = self.env['notices.notices'].
        
        _logger.warning('Entramos a metodo de crear aviso')
        
        
        