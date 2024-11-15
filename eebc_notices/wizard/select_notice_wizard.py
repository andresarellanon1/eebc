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
        string='notices_id',
        comodel_name='notices.notices',
        domain=lambda self: self._get_notice_domain()
)
    
    
    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
            
            
        return res

    def _get_notice_domain(self):
        """Get domain to filter notices based on cantidad"""
        return [('quantity', '>=', 0),('stock_location_origin_id','=',self._context['location_id'])] if self.quantity else []
    
   