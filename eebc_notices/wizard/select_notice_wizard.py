# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError



import logging

_logger = logging.getLogger(__name__)

class SelectNoticeWizard(models.TransientModel):
    _name = "select.notice.wizard"
    _description = "Wizard where we will select the notice to take the product"

    
    quantity = fields.Float(string="Cantidad", readonly=True,)
    stock_picking_location_id = fields.Integer(
        string='id almacen',
    )

    line_ids = fields.One2many('wizard.selection.line', 'wizard_id', string='Lines')
    selected_records_count = fields.Integer(string='Selected Records', compute='_compute_selected_records_count')

    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'location_id' in self._context:
            res['stock_picking_location_id'] = self._context['location_id']
        
        _logger.warning('res value: %s', res)
        return res
    

    @api.depends('line_ids')
    def _compute_selected_records_count(self):
        for wizard in self:
            _logger.warning('id value2: %s', wizard.id)
            
            wizard.selected_records_count = len(wizard.line_ids)


    def action_get_products(self):
        _logger.warning('id value2: %s', self.id)
        
        for line in self.line_ids:
            record = line.record_id
            quantity = line.quantity
            _logger.warning(f"Processing record {record.display_name} with quantity {quantity}")
        
        self.active = False
        return {'type': 'ir.actions.act_window_close'}

    
   
   