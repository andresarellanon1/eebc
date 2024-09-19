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
        
       # Aquí el registro 'self' es el stock.move en el que se hizo clic
        _logger.warning('Entramos al método de crear aviso para el movimiento: %s', self.id)

        # Puedes acceder a los datos de la línea (stock.move) que recibió el clic
        _logger.warning('Producto: %s', self.product_id)
        _logger.warning('Cantidad: %s', self.product_uom_qty)
        _logger.warning('Parner: %s', self.picking_id.partner_id)
        

        # Crear el aviso relacionado a partir de los datos del movimiento
        notice_vals = {
            'description': 'Aviso generado para el producto %s en la operación %s' % (self.product_id.name, self.picking_id.name),
            'quantity': self.product_uom_qty,
            'resource': self.product_id,
            'supplier': self.picking_id.partner_id,
            'description': self.product_id.description,
            
            # Otros valores que quieras pasar a notices.notices
        }
        _logger.warning('VALS PARA AVISO: %s', notice_vals)
        
        
        notice = self.env['notices.notices'].create(notice_vals)
        _logger.warning('Se ha creado el aviso con ID: %s', notice.id)
        


