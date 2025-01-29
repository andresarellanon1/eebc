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
    single_notice = fields.Boolean(string="Un solo aviso", default=False)
    multiple_notice = fields.Boolean(string="Multiples avisos", default=False)
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
        """Crea nuevos registros en el modelo notices.notices basado en los datos extraídos del archivo."""

        # Validación de opciones seleccionadas
        if self.update_tab and self.create_tab:
            raise ValidationError("Debe elegir una sola opción entre crear o actualizar aviso.")
        
        if not self.create_tab:
            raise ValidationError("Debe marcar la casilla 'Crear aviso' para proceder.")

        if not self.notice or not self.folio:
            raise ValidationError("Debe completar los campos 'Aviso' y 'Folio' antes de continuar.")

        _logger.warning('Iniciando creación de avisos...')

        # Buscar si el aviso ya existe
        existing_notice = self.env['notices.notices'].search([('notice', '=', self.notice)])

        # Validar si hay duplicados en el historial
        if existing_notice:
            history_match = existing_notice.history_ids.filtered(lambda h: int(h.folio) == int(self.folio))
            if history_match:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'notice.file.wizard',
                    'view_mode': 'form',
                    'view_id': self.env.ref('eebc_notices.wizard_notice_error').id,
                    'target': 'new',
                    'context': {
                        'default_message': f"El folio {self.folio} ya está registrado en el aviso {existing_notice.notice}.",
                    }
                }

        # Manejo de la opción SINGLE_NOTICE (Un solo aviso para todos los lotes)
        if self.single_notice:
            _logger.warning("Creando un solo aviso con todos los números de serie/lote...")
            
            # Obtener todos los lotes asociados al `stock_move_id`
            lot_ids = self.stock_move_id.lot_ids.ids if self.stock_move_id else []

            if not lot_ids:
                raise ValidationError("No hay lotes asociados al traslado seleccionado.")

            # Crear un único aviso con todos los lotes
            notice = self.env['notices.notices'].create({
                'product_id': self._context['product_id'],
                'quantity': self.quantity,
                'description': self.description,
                'partner_id': self._context['proveedor_id'],
                'notice': self.notice,
            })

            # Crear historial con todos los lotes
            self.env['notices.history'].create({
                'location_id': self._context['location_id'],
                'location_dest': self._context['location_dest_id'],
                'product_id': self._context['product_id'],
                'quantity': self.quantity,
                'picking_code': self._context['type'],
                'notice_id': notice.id,
                'folio': self.folio,
                'origin': self._context['origin'],
                'purchase_order_id': self._context['purchase_order_id'],
                'sale_order_id': self._context['sale_ids'],
                'stock_move_id': self._context['stock_move_id'],
                'state': 'draft',
                'lot_ids': [(6, 0, lot_ids)],  # Asignar todos los lotes al aviso
            })

        # Manejo de la opción MULTIPLE_NOTICE (Un aviso por cada número de serie/lote)
        elif self.multiple_notice:
            _logger.warning("Creando múltiples avisos, uno por cada número de serie/lote...")

            # Obtener cada lote del `stock_move_id`
            for lot in self.stock_move_id.lot_ids:
                # Crear un aviso para cada lote
                notice = self.env['notices.notices'].create({
                    'product_id': self._context['product_id'],
                    'quantity': self.quantity / len(self.stock_move_id.lot_ids),  # Distribuir la cantidad
                    'description': self.description,
                    'partner_id': self._context['proveedor_id'],
                    'notice': f"{self.notice} - {lot.name}",  # Nombre del aviso con el lote
                })

                # Crear historial vinculado al aviso
                self.env['notices.history'].create({
                    'location_id': self._context['location_id'],
                    'location_dest': self._context['location_dest_id'],
                    'product_id': self._context['product_id'],
                    'quantity': self.quantity / len(self.stock_move_id.lot_ids),
                    'picking_code': self._context['type'],
                    'notice_id': notice.id,
                    'folio': f"{self.folio}-{lot.name}",  # Folio único por lote
                    'origin': self._context['origin'],
                    'purchase_order_id': self._context['purchase_order_id'],
                    'sale_order_id': self._context['sale_ids'],
                    'stock_move_id': self._context['stock_move_id'],
                    'state': 'draft',
                    'lot_ids': [(6, 0, [lot.id])],  # Asignar solo el lote correspondiente
                })

        else:
            raise ValidationError("Debe seleccionar 'Un solo aviso' o 'Múltiples avisos' para continuar.")

        # Limpieza del contexto y redirección
        self = self.with_context(lot_ids=False)
        return self.stock_move_id.action_show_incoming()
            











    # @api.constrains('notice_ids')  # Decorador que valida automáticamente
    def _check_quantities(self):
        for wizard in self:
            total = sum(line.quantity for line in wizard.notice_ids)
            if total != wizard.quantity:
                raise ValidationError(
                    f"La cantidad y la demanda deben coincidir. Cantidad total asignada: {total} / Demanda: {wizard.quantity}"
                )
            


