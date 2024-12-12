# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError




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

    stock_move_id = fields.Many2one('stock.move', string='Traslado')

   
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
        if 'stock_move_id' in self._context:
            res['stock_move_id'] = self._context['stock_move_id']
        if 'lines' in self._context:
            res['notice_ids'] = self._context['lines']
        _logger.warning('vALORDE LINEASS RES : %s',res)
        _logger.warning('VALOR DE RES1: %s', res)
        return res


   
    @api.onchange('create_tab','update_tab')
    def onchange_create_tab_update_tab(self):
        _logger.warning('entramos al onchange')
        if not self.create_tab:
            _logger.warning('entramos al onchange create_tab')

            
            self.write({
                'notice': '',
                'folio': ''
            })
        if not self.update_tab:
            _logger.warning('entramos al onchange update_tab')

            if self.notice_ids:
                    self.notice_ids = [(1, line.id, {'quantity': 0}) for line in self.notice_ids]
        

    def create_notice(self):
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo"""            

        notice_id = self.env['notices.notices'].search([('notice', '=', self.notice)])
        

        if self.update_tab and self.create_tab:
            raise ValidationError("Debe eleguir una sola tarea a ejecutar entre crear o actualizar aviso")
        
        elif self.create_tab:
            if not self.notice or not self.folio:
                raise ValidationError('No a llenado los campos necesarios para crear un nuevo aviso')
            _logger.warning('Creamos')
            if notice_id:
                history_match = notice_id.history_ids.filtered(lambda h: int(h.folio) == self.folio)
                if history_match:
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'notice.file.wizard',
                        'view_mode': 'form',
                        'view_id': self.env.ref('eebc_notices.wizard_notice_error').id,
                        'target': 'new',
                        'context': {
                            'default_message': f"El folio del archivo ({self.folio}) ya existe en el folio ({notice_id}).",
                        }
                    }
                else:
                    notice_id.write({
                        'history_ids': [(0, 0, {
                            'location_dest': self._context['location_dest_id'],
                            'location_id': self._context['location_id'],
                            'product_id': self._context['product_id'],
                            'quantity': self.quantity,
                            'folio': self.folio,
                            'picking_code': self._context['type'],
                            'origin': self._context['origin'],
                            'purchase_order_id':self._context['purchase_order_id'],
                            'sale_order_id':self._context['sale_ids'],
                            'state': 'draft',

                        })]
                    })
            else:
                notice = self.env['notices.notices'].create({
                    'product_id': self._context['product_id'],
                    'quantity': self.quantity,
                    'description': self.description,
                    'partner_id': self._context['proveedor_id'],
                    'notice': self.notice,
                })
                self.env['notices.history'].create({
                    'location_id': self._context['location_id'],
                    'location_dest': self._context['location_dest_id'],
                    'product_id': self._context['product_id'],
                    'quantity': self.quantity,
                    'picking_code': self._context['type'],
                    'notice_id': notice.id,
                    'folio': self.folio,
                    'origin': self._context['origin'],
                    'purchase_order_id':self._context['purchase_order_id'],
                    'sale_order_id':self._context['sale_ids'],
                    'stock_move_id':self._context['stock_move_id'],
                    'state': 'draft',
                    
                })
                
                # bool_notice_established = self.env['stock.move'].search([('id','=', self._context['stock_move_id'])]).notice_established
                # if bool_notice_established:
                #     _logger.warning(f'Se cumple if de bool_notice_established, valor: {bool_notice_established}')
                #     bool_notice_established = True
                    
            # Limpieza del contexto
            self = self.with_context(
                lot_ids=False
            )


            return {
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'notice.file.wizard',
                        'target': 'new',
                        'res_id': self.id,
                    }
        elif self.update_tab:
            _logger.warning('Actualizamos')
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
                                    'quantity': line.quantity,
                                    'picking_code': wizard.stock_move_id.picking_id.picking_type_code,
                                    'origin': wizard.stock_move_id.picking_id.sale_id.name,
                                    'sale_order_id': wizard.stock_move_id.picking_id.sale_id.id,
                                    'product_id': wizard.stock_move_id.product_id.id,
                                    'purchase_order_id': self._context.get('purchase_order_id'),
                                    'state': 'draft',
                                    'stock_move_id': self._context['stock_move_id'],

                                })]
                            })

                    _logger.warning('Se procesaron todas las líneas de notice_ids.')
                
                # Retornar para cerrar la ventana
                    return {
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'notice.file.wizard',
                        'target': 'new',
                        'res_id': self.id,
                    }

            except ValidationError as e:
                # Registrar el mensaje de error para depuración
                _logger.error(f"ValidationError detectado: {e}")
                raise  # Propaga el ValidationError para que se muestre en la interfaz del usuario

            except Exception as e:
                # Manejar otros errores inesperados
                _logger.error(f"Error en action_get_products: {e}")
                raise  # Propaga otros errores si es necesario
        

        
        else:
            raise ValidationError("Debe marcar una casilla")
            











    # @api.constrains('notice_ids')  # Decorador que valida automáticamente
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
                        'name': line.aviso_name,  # Ajusta 'name' al campo que contiene el nombre del aviso
                        'available': line.quantity_available,
                        'established': line.quantity
                    })            
            if notices_list:
                message = "Los siguientes avisos tienen cantidades que exceden las disponibles:\n"
                for notice in notices_list:
                    message += f"- {notice['name']}: {notice['available']} disponibles / {notice['established']} establecidos\n"
                
                raise ValidationError(message)


