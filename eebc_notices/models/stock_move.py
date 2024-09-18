from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    def create_notice(self):
        
        # notice = self.env['notices.notices'].
        
        _logger.warning('Entramos a metodo de crear aviso')
        



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    has_aviso_in_attributes = fields.Boolean(
        string="Tiene 'aviso' en atributos",
        compute='_compute_has_aviso_in_attributes'
    )

    @api.depends('move_ids_without_package.product_id.attribute_line_ids')
    def _compute_has_aviso_in_attributes(self):
        for record in self:
            record.has_aviso_in_attributes = any(
                'aviso' in attr.name for move in record.move_ids_without_package for attr in move.product_id.attribute_line_ids.mapped('attribute_id')
            )