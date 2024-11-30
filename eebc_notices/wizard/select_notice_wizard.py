# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError



import logging

_logger = logging.getLogger(__name__)

class SelectNoticeWizard(models.TransientModel):
    _name = "select.notice.wizard"
    _description = "Wizard where we will select the notice to take the product"

    notice_ids = fields.One2many(
        'wizard.selection.line',
        'wizard_id',
        string='Avisos',
         
    )
    quantity = fields.Float(string="Demanda total", readonly=True,)
    stock_move_id = fields.Many2one('stock.move', string='Traslado')

    @api.model
    def default_get(self, fields):
        res = super(SelectNoticeWizard, self).default_get(fields)
        if 'stock_move_id' in self._context:
            res['stock_move_id'] = self._context['stock_move_id']
        if 'cantidad' in self._context:
            res['quantity'] = self._context['cantidad']
        if 'lines' in self._context:
            res['notice_ids'] = self._context['lines']
        _logger.warning('vALORDE LINEASS RES : %s',res)
        
        return res
    

    def action_get_products(self):
        try:
            for wizard in self:
                _logger.warning('Inicio del proceso en wizard.')

                # Validar cantidades (puede lanzar un ValidationError)
                self._check_quantities()

                # Iterar sobre notice_ids
                for line in wizard.notice_ids:
                    for notice in line.notice_id:
                        # Validar datos necesarios antes de proceder
                        if not wizard.stock_move_id or not wizard.stock_move_id.picking_id:
                            _logger.error("El campo stock_move_id o picking_id no está definido.")
                            raise ValueError("Faltan datos necesarios en stock_move_id o picking_id.")

                        # Escribir el historial
                        notice.write({
                            'history_ids': [(0, 0, {
                                'location_id': wizard.stock_move_id.picking_id.location_id.id,
                                'location_dest': wizard.stock_move_id.picking_id.location_dest_id.id,
                                'quantity': line.quantity * (-1),
                                'picking_code': wizard.stock_move_id.picking_id.picking_type_code,
                                'origin': wizard.stock_move_id.picking_id.sale_id.name,
                                'sale_order_id': wizard.stock_move_id.picking_id.sale_id.id,
                                'product_id': wizard.stock_move_id.product_id.id,
                                'purchase_order_id': self._context.get('purchase_order_id'),
                                'state': 'draft',
                                'stock_move_id': wizard.stock_move_id,

                            })]
                        })

                _logger.warning('Se procesaron todas las líneas de notice_ids.')
            
            # Retornar para cerrar la ventana
            return {'type': 'ir.actions.act_window_close'}

        except ValidationError as e:
            # Registrar el mensaje de error para depuración
            _logger.error(f"ValidationError detectado: {e}")
            raise  # Propaga el ValidationError para que se muestre en la interfaz del usuario

        except Exception as e:
            # Manejar otros errores inesperados
            _logger.error(f"Error en action_get_products: {e}")
            raise  # Propaga otros errores si es necesario



   


    @api.constrains('notice_ids')  # Decorador que valida automáticamente
    def _check_quantities(self):
        for wizard in self:
            total = sum(line.quantity for line in wizard.notice_ids)
            if total != wizard.quantity:
                raise ValidationError(
                    f"La cantidad y la demanda deben coincidir. Cantidad total asignada: {total} / Demanda: {wizard.quantity}"
                )
            notices_list = []
            for line in wizard.notice_ids:        
                if line.quantity > line.quantity_available:
                    notices_list.append({
                        'name': line.test_name,  # Ajusta 'name' al campo que contiene el nombre del aviso
                        'available': line.quantity_available,
                        'established': line.quantity
                    })            
            if notices_list:
                message = "Los siguientes avisos tienen cantidades que exceden las disponibles:\n"
                for notice in notices_list:
                    message += f"- {notice['name']}: {notice['available']} disponibles / {notice['established']} establecidos\n"
                
                raise ValidationError(message)

# Requerimento(?) salidas parciales - Caso en el que la demanda total es mayor a la cantidad total de



            


    
   
   