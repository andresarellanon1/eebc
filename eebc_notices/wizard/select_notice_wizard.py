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
    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'location_id' in self._context:
            res['stock_picking_location_id'] = self._context['location_id']
        
        
            
        _logger.warning('id value: %s', self.id)
        
        _logger.warning('res value: %s', res)
        return res
    
    # notices_id = fields.Many2one(
    #     'notices.notices',
    #     string='notices_id',
    #     domain=lambda self: self._get_notice_domain()
    # )
    line_ids = fields.One2many('wizard.selection.line', 'wizard_id', string='Lines')
    selected_records_count = fields.Integer(string='Selected Records', compute='_compute_selected_records_count')


    @api.depends('line_ids')
    def _compute_selected_records_count(self):
        for wizard in self:
            wizard.selected_records_count = len(wizard.line_ids)


    # def _get_notice_domain(self):
    #     """Get domain to filter notices based on cantidad"""
    #     return [('quantity', '>', 0), ('stock_location_origin_id', '=', self._context.get('location_id'))] if self.quantity else []

    def action_get_products(self):
        for line in self.line_ids:
            record = line.record_id
            quantity = line.quantity
            _logger.warning(f"Processing record {record.display_name} with quantity {quantity}")
        return {'type': 'ir.actions.act_window_close'}

    
   
   