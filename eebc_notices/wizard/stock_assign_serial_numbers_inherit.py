from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockAssignSerialNumbers(models.TransientModel):
    _inherit= 'stock.assign.serial'
    _description = 'Stock Assign Serial Numbers Inherit'

    is_aviso = fields.Boolean(string = "Es aviso", default = False)

    @api.model
    def default_get(self, fields_list):
        _logger.warning('Entra a default_get en StockAssignSerialNumbers')
        res = super(StockAssignSerialNumbers, self).default_get(fields_list)
        # has_aviso = self.env.context.get('is_aviso')

        if 'is_aviso' in self._context:
            res['is_aviso'] = self._context['is_aviso']
       

        _logger.warning(f'Valores is_aviso en res: {res.get("is_aviso")}')
        return res


    def generate_serial_numbers(self):
        self.ensure_one()
        self.move_id.next_serial = self.next_serial_number or ""
        return self.move_id._generate_serial_numbers(self.next_serial_number, next_serial_count=self.next_serial_count)
