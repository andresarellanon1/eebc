from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):

    _inherit= 'product.template'    


    
    crea_aviso = fields.Boolean(
        string='crea_aviso',
        
            compute='_compute_crea_aviso' )
        

    @api.depends('attribute_line_ids')
    def _compute_crea_aviso(self):
        _logger.warning('Entramos a compute _compute_crea_aviso')
        for record in self:
            record.crea_aviso = False

            for attribute_line in record.attribute_line_ids:
                if any(value.name == 'Con aviso' for value in attribute_line.value_ids):
                    record.crea_aviso = True
                    break  # Detener la búsqueda si se encuentra el valor
            _logger.warning('valor boleano crear aviso: %s', record.crea_aviso)
            

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_aviso = fields.Boolean(
        string='Es aviso',
        related='product_tmpl_id.crea_aviso',
        store=True,
        readonly=True,
    )