# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError

import base64
import pandas as pd
import io

import logging

_logger = logging.getLogger(__name__)

# TODO: 
# Falta agregar los campos recurso, serie y fecha
# Agregar a la vista del wizard la cantidad de la linea de la orden de compra y la cantidad que esta en el excel del respectivo producto al cual se le desea crear aviso. - LISTO (?)

class NoticeFileWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a fsm.person or
     fsm.location
    """

    _name = "notice.file.wizard"
    _description = "Wizard to recover data from xlsx file"
    
    quantity = fields.Float(string="Cantidad", readonly=True,)
    message = fields.Text(string="Mensaje de Error", readonly=True)  # Campo para el mensaje de error
    notice = fields.Char(string='Aviso')
    folio = fields.Char(string='Folio')
    description = fields.Text(string='Descripción de producto', readonly=True)
  # Cambiar el campo Many2one por Char para almacenar el ID o el nombre de la factura
    account_move_invoice_ids = fields.Char(string="Facturas", readonly=True)

    # Cambiar One2many a Char para almacenar IDs o nombres de proveedores
    res_partner_supplier_id = fields.Char(string="Proveedor", readonly=True)

    # Cambiar One2many a Char para almacenar IDs o referencias de órdenes de compra
    purchases_order_id = fields.Char(string="Orden de compra", readonly=True)
    
    
    @api.model
    def default_get(self, fields):
        res = super(NoticeFileWizard, self).default_get(fields)
        
        # Establecer el valor del campo 'quantity' con el valor pasado en el contexto
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
        
        return res

        	
     

    def create_notice(self):
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo"""
        
        notice_data = (self.quantity,                           
                       self.res_partner_supplier_id,
                       self.purchases_order_id, 
                       self.description,
                       self.folio,
                       self.notice, 
                       self.account_move_invoice_ids, 
                       self._context['product_id'], 
                       self._context['location_id'], 
                       self._context['location_dest_id'], 
                       self._context['origin'], 
                       self._context['type']
                       )
        
        

        _logger.warning('VALORES DE NOTICE DATA:  %s', notice_data)
        
        for data in notice_data:
            its_created = self.env['notices.notices'].search([('notice','=', self.notice)])
            _logger.warning('VALOR DE ITS CREATED : %s', its_created)
            valor_test =  self.folio

            if its_created:
                _logger.warning('1')
                _logger.warning('VALOR DE ITS CREATED folio : %s', its_created.folio)

                _logger.warning('VALOR DE data folio : %s', valor_test)

                for i in its_created.history_ids:
                    _logger.warning('valor de registro : %s', i)

                    _logger.warning('valor de registro folio: %s', i.folio)

                history_match = its_created.history_ids.filtered(lambda h: int(h.folio) == valor_test)
                _logger.warning('valor de history match: %s', history_match)

                if history_match:
                     _logger.warning('2')

                     return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'notice.file.wizard',
                        'view_mode': 'form',
                        'view_id': self.env.ref('eebc_notices.wizard_notice_error').id,
                        'target': 'new',
                        'context': {
                            'default_message': f"El folio del archivo ({valor_test}) ya existe en el folio ({its_created}).",
                        }
                        
                    }
                else:
                    _logger.warning('3')
                    _logger.warning('No se encontró ningún registro en history_ids con folio: %s', valor_test)
                    its_created.write({
                    'history_ids': [(0, 0, {
                        'location_dest': data[9],  # Añade los campos necesarios para history
                        'location_id': data[8],
                        'quantity': data[0],
                        'folio': data[4],
                        'picking_code': data[11],
                        })]
                    })

                    _logger.info('Historial actualizado correctamente para el aviso.')
            else:
                _logger.warning('4')

                # Crear el nuevo registro en el modelo 'notices.notices'
                notice = self.env['notices.notices'].create({
                    'resource': data[7],  # ID del producto
                    'quantity': data[0],  # Cantidad extraída del archivo
                    'description': data[3],
                    'supplier': data[1],
                    'notice': data[5],
                    
                    
                })

                self.env['notices.history'].create({
                    'location_id': data[8], 
                    'location_dest': data[9], 
                    'quantity': data[0],  # Cantidad extraída del archivo
                    'picking_code': data[11],
                    'notice_id':notice.id,
                    'folio':data[4],
                    
                    
                    
                })



        _logger.info(f"{len(notice_data)} avisos creados correctamente.")

        
        
 
        





