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
        for wizard in self:
            _logger.warning('first for')
            self._check_quantities()
            for line in wizard.notice_ids:
                for notice in line.notice_id:
                    notice.sudo().write({
                        'history_ids': [(0, 0, {
                            'location_id': wizard.stock_move_id.picking_id.location_id.id,
                            'location_dest_id': wizard.stock_move_id.picking_id.location_dest_id.id,
                            'quantity': line.quantity * (-1),
                            'picking_code': wizard.stock_move_id.picking_id.picking_type_code,
                            'origin': wizard.stock_move_id.picking_id.sale_id.name,
                            'sale_order_id': wizard.stock_move_id.picking_id.sale_id.id,
                            'product_id': wizard.stock_move_id.product_id.id,
                            'folio': notice.folio,
                            'purchase_order_id':self._context['purchase_order_id']
                        })]
                    })

        return {'type': 'ir.actions.act_window_close'}


    @api.constrains('notice_ids')
    def _check_quantities(self):
        for wizard in self:
            # Validar el total asignado
            total = sum(line.quantity for line in wizard.notice_ids)
            _logger.warning('Valor de total desde notice_ids: %s', total)

            if total != wizard.quantity:
                raise ValidationError(
                    f"La cantidad y la demanda deben coincidir. Cantidad asignada: {total} / Demanda: {wizard.quantity}"
                )

            # Lista para inconsistencias
            notices_list = []

            # Obtener líneas del contexto
            context_lines = wizard._context.get('lines', [])
            _logger.warning('Líneas obtenidas desde el contexto: %s', context_lines)

            # Validar cantidades combinando notice_ids y context_lines
            for line in wizard.notice_ids:
                _logger.warning('Procesando línea con notice_id: %s', line.notice_id.id)

                # Buscar datos en context_lines basados en notice_id
                notice_data = next((data[2] for data in context_lines if data[2]['notice_id'] == line.notice_id.id), None)
                
                if notice_data:
                    _logger.warning('Datos del aviso desde contexto: %s', notice_data)
                    
                    # Comparar quantity del One2many con quantity_available del contexto
                    if line.quantity > notice_data['quantity_available']:
                        _logger.warning('Se cumple la condición de cantidad excedida')
                        notices_list.append({
                            'name': line.test_name,
                            'available': notice_data['quantity_available'],
                        })
                else:
                    _logger.warning(f'No se encontró información de contexto para notice_id: {line.notice_id.id}')

            # Generar mensaje de error si hay inconsistencias
            if notices_list:
                message = "Los siguientes avisos tienen cantidades que exceden las disponibles:\n"
                for notice in notices_list:
                    message += f"- {notice['name']}: {notice['available']} disponibles\n"
                
                raise ValidationError(message)


    # @api.constrains('notice_ids')  # Decorador que valida automáticamente
    # def _check_quantities(self):
    #     for wizard in self:
    #         total = sum(line.quantity for line in wizard.notice_ids)
    #         _logger.warning('Valor de total: %s', total)

    #         if total != wizard.quantity:
    #             raise ValidationError(
    #                 f"La cantidad y la demanda deben coincidir. Cantidad asignada: {total} / Demanda: {wizard.quantity}"
    #             )
    #         notices_list = []
    #         notices_list_v2 = wizard._context.get('lines', [])
    #         _logger.warning('lista valores: %s', notices_list_v2)

    #         for line in wizard.notice_ids:
                
    #             _logger.warning(f'nombre {line.test_name} cantidad disponible: {line.quantity_available} cantidad establecida: {line.quantity}')
        
    #             if line.quantity > line.quantity_available:
    #                 _logger.warning('se cumpole if')
    #                 notices_list.append({
    #                     'name': line.test_name,  # Ajusta 'name' al campo que contiene el nombre del aviso
    #                     'available': line.quantity_available,
    #                 })
    #         _logger.warning('Valor de lista: %s', notices_list)
            
    #         if notices_list:
    #             # Construir el mensaje del ValidationError
    #             message = "Los siguientes avisos tienen cantidades que exceden las disponibles:\n"
    #             for notice in notices_list:
    #                 message += f"- {notice['name']}: {notice['available']} disponibles\n"
                
    #             raise ValidationError(message)



            


    
   
   