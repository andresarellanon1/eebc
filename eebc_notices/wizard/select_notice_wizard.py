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
    notices_id = fields.Many2one(
        'notices.notices',
        string='notices_id',
        domain=lambda self: self._get_notice_domain()
    )
    line_ids = fields.One2many('wizard.selection.line', 'wizard_id', string='Lines')
    selected_records_count = fields.Integer(string='Selected Records', compute='_compute_selected_records_count')
    stock_picking_location_id = fields.Integer(
        string='id almacen',
    )
    
    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'location_id' in self._context:
            res['stock_picking_location_id'] = self._context['location_id']
        if 'proveedor' in self._context:
            res['res_partner_supplier_id'] = self._context['proveedor']
        if 'origin' in self._context:
            res['purchases_order_id'] = self._context['origin']
        if 'product_description' in self._context:
            res['description'] = self._context['product_description']
        if 'invoices' in self._context:
            res['account_move_invoice_ids'] = self._context['invoices']
        if 'default_message' in self._context:
            res['message'] = self._context['default_message']  # Asignar el mensaje de error desde el contexto
        return res


    @api.depends('stock_picking_location_id')
    def _compute_stock_picking_location_id(self):
        _logger.warning("Entramos coocapsmcsa")

        
        self.stock_picking_location_id = self._context['location_id']

        _logger.warning("Calor dede self stock puinckin: %s",  self.stock_picking_location_id)


    @api.depends('line_ids')
    def _compute_selected_records_count(self):
        for wizard in self:
            wizard.selected_records_count = len(wizard.line_ids)

    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
        return res

    def _get_notice_domain(self):
        """Get domain to filter notices based on cantidad"""
        return [('quantity', '>', 0), ('stock_location_origin_id', '=', self._context.get('location_id'))] if self.quantity else []

    def action_get_products(self):
        for line in self.line_ids:
            record = line.record_id
            quantity = line.quantity
            _logger.warning(f"Processing record {record.display_name} with quantity {quantity}")
        return {'type': 'ir.actions.act_window_close'}

    
   
   