from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'


    has_aviso_in_attributes = fields.Boolean(
        string="Tiene 'aviso' en atributos",
        compute='_compute_has_aviso_in_attributes'
    )

    @api.depends('product_id.attribute_line_ids')
    def _compute_has_aviso_in_attributes(self):
        for move in self:
            move.has_aviso_in_attributes = any(
                'aviso' in attr.name for attr in move.product_id.attribute_line_ids.mapped('attribute_id')
            )
    
    
    def create_notice(self):
        
        # notice = self.env['notices.notices'].
        
        _logger.warning('Entramos a metodo de crear aviso')

        


