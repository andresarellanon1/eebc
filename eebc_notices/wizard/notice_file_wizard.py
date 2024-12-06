# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError



import logging

_logger = logging.getLogger(__name__)


class NoticeFileWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "notice.file.wizard"
    _description = "Wizard to recover data from xlsx file"
    
    notice_ids = fields.One2many(
        'wizard.selection.line',
        'wizard_crud_id',
        string='Avisos',
         
    )

    create_tab = fields.Boolean(string="Crear aviso", default=False)
    update_tab = fields.Boolean(string="Actualizar aviso", default=False)


   
    quantity = fields.Float(string="Cantidad", readonly=True,)
    message = fields.Text(string="Mensaje de Error", readonly=True)  # Campo para el mensaje de error
    notice = fields.Char(string='Aviso')
    folio = fields.Char(string='Folio')
    description = fields.Text(string='Descripción de producto', readonly=True)
    account_move_invoice_ids = fields.Char(string="Facturas", readonly=True)
    res_partner_supplier_id = fields.Char(string="Proveedor", readonly=True)
    purchases_order_id = fields.Char(string="Orden de compra", readonly=True)
    
    @api.model
    def default_get(self, fields):
        res = super(NoticeFileWizard, self).default_get(fields)
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
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
        if 'lines' in self._context:
            res['notice_ids'] = self._context['lines']
        _logger.warning('vALORDE LINEASS RES : %s',res)
        _logger.warning('VALOR DE RES1: %s', res)
        return res


   
    @api.onchange('create_tab', 'update_tab')
    def _onchange_create_tab_update_tab(self):

        self.notice = False
        self.folio = False
        # Recorre las líneas en notice_ids y establece quantity en 0
        for line in self.notice_ids:
            line.quantity = 0
            _logger.info(f"Línea actualizada: {line.id}, cantidad: {line.quantity}")


    
    # @api.onchange('update_tab')
    # def _onchange_update_tab(self):
    #     pass
        
    
    
    

    def create_notice(self):
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo"""
        pass
            

        # notice_id = self.env['notices.notices'].search([('notice', '=', self.notice)])
        
        

        # if notice_id:
        #     history_match = notice_id.history_ids.filtered(lambda h: int(h.folio) == self.folio)
        #     if history_match:
        #         return {
        #             'type': 'ir.actions.act_window',
        #             'res_model': 'notice.file.wizard',
        #             'view_mode': 'form',
        #             'view_id': self.env.ref('eebc_notices.wizard_notice_error').id,
        #             'target': 'new',
        #             'context': {
        #                 'default_message': f"El folio del archivo ({self.folio}) ya existe en el folio ({notice_id}).",
        #             }
        #         }
        #     else:
        #         notice_id.write({
        #             'history_ids': [(0, 0, {
        #                 'location_dest': self._context['location_dest_id'],
        #                 'location_id': self._context['location_id'],
        #                 'product_id': self._context['product_id'],
        #                 'quantity': self.quantity,
        #                 'folio': self.folio,
        #                 'picking_code': self._context['type'],
        #                 'origin': self._context['origin'],
        #                 'purchase_order_id':self._context['purchase_order_id'],
        #                 'sale_order_id':self._context['sale_ids'],
        #                 'state': 'draft',

        #             })]
        #         })
        # else:
        #     notice = self.env['notices.notices'].create({
        #         'product_id': self._context['product_id'],
        #         'quantity': self.quantity,
        #         'description': self.description,
        #         'partner_id': self._context['proveedor_id'],
        #         'notice': self.notice,
        #     })
        #     self.env['notices.history'].create({
        #         'location_id': self._context['location_id'],
        #         'location_dest': self._context['location_dest_id'],
        #         'product_id': self._context['product_id'],
        #         'quantity': self.quantity,
        #         'picking_code': self._context['type'],
        #         'notice_id': notice.id,
        #         'folio': self.folio,
        #         'origin': self._context['origin'],
        #         'purchase_order_id':self._context['purchase_order_id'],
        #         'sale_order_id':self._context['sale_ids'],
        #         'stock_move_id':self._context['stock_move_id'],
        #         'state': 'draft',
                
        #     })
            
        #     # bool_notice_established = self.env['stock.move'].search([('id','=', self._context['stock_move_id'])]).notice_established
        #     # if bool_notice_established:
        #     #     _logger.warning(f'Se cumple if de bool_notice_established, valor: {bool_notice_established}')
        #     #     bool_notice_established = True
                
        # # Limpieza del contexto
        # self = self.with_context(
        #     lot_ids=False
        # )

