from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProductReplenishInherit(models.TransientModel):
    _inherit = 'product.replenish'

    is_aviso = fields.Boolean(string="Es aviso", compute="_compute_is_aviso")

    @api.depends('product_id')
    def _compute_is_aviso(self):
        """Detecta si el producto tiene el atributo 'Con aviso'"""
        for record in self:
            has_aviso = any(value.name == 'Con aviso' for value in record.product_id.attribute_line_ids.mapped('value_ids'))
            record.is_aviso = has_aviso
            _logger.warning(f"Producto {record.product_id.name} tiene aviso: {record.is_aviso}")

    def launch_replenishment(self):
        """Si el producto tiene aviso, mostrar wizard para capturar los datos"""
        if self.is_aviso:
            return {
                'name': 'Configurar Aviso',
                'type': 'ir.actions.act_window',
                'res_model': 'product.replenish.aviso.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_replenish_id': self.id,
                    'default_quantity': self.quantity,
                    'default_product_id': self.product_id.id
                }
            }
        return super().launch_replenishment()