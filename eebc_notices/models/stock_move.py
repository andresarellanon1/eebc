from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)



class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type_codigo = fields.Selection(
        related='picking_type_id.code',
        readonly=True
    )
    show_incoming_button = fields.Boolean(
        string="Mostrar botón de entrada",
        compute='_compute_aviso_button_flags',
    )
    show_outgoing_button = fields.Boolean(
        string="Mostrar botón de salida",
        compute='_compute_aviso_button_flags',
    )

    @api.depends('product_id.attribute_line_ids', 'picking_type_id.code', 'product_id')
    def _compute_aviso_button_flags(self):
        for move in self:
            has_aviso = any('aviso' in attr.name for attr in move.product_id.attribute_line_ids.mapped('attribute_id'))
            is_valid_picking_type = move.picking_type_id.code in ['incoming', 'outgoing']
            if has_aviso and is_valid_picking_type:
                _logger.warning('ENTRAMOS A IF')
                move.show_incoming_button = move.picking_type_id.code == 'incoming'
                move.show_outgoing_button = move.picking_type_id.code == 'outgoing'
                _logger.warning('move.show_outgoing_button: %s', move.show_outgoing_button)
                _logger.warning('move.show_incoming_button: %s', move.show_incoming_button)
                
            else:
                _logger.warning('ENTRAMOS A ELSE')
                
                move.show_incoming_button = False
                move.show_outgoing_button = False



 

    def action_show_incoming(self):
        order = self.env['purchase.order'].search([('name', '=', self.origin)])
        invoice_names = ", ".join(order.invoice_ids.mapped('name')) if order.invoice_ids else "No hay facturas"
        proveedor_name = self.picking_id.partner_id.name if self.picking_id.partner_id else "Proveedor no definido"
        proveedor_id = self.picking_id.partner_id.id if self.picking_id.partner_id else False
        purchase_order_id = order.id if order else False
        product_description = self.description_picking if self.description_picking else "Sin descripción"
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wizard File Upload',
            'res_model': 'notice.file.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('eebc_notices.wizard_notice_file_view').id,  # Aquí se especifica el ID correcto de la vista
            'target': 'new',
            'context': {
                'product_id': self.product_id.id,  # Pasar valores por defecto
                'cantidad':  self.product_uom_qty,
                'proveedor': proveedor_name,  # Pasar el nombre del proveedor
                'proveedor_id': proveedor_id,
                'type': self.picking_id.picking_type_code,
                'location_id': self.picking_id.location_id.id,
                'location_dest_id': self.picking_id.location_dest_id.id,
                'origin': self.picking_id.origin,
                'lot_ids':self.lot_ids,
                'purchase_order_id': purchase_order_id,
                'sale_ids': order._get_sale_orders().ids if order else False,
                'date_aprovee': order.date_approve,
                'product_description':product_description,
                'invoices': invoice_names , # Pasar los nombres de las facturas
                'stock_move_id':self.id
                
            }
        }
        
    def action_show_outgoing(self):
        _logger.warning('valor del pickinf id: %s', self.picking_id.location_id.id)

        notice_lines_to_wizard =self._create_line_ids()
        _logger.warning('Valor de las lineas : %s', notice_lines_to_wizard)
        order = self.env['purchase.order'].search([('name', '=', self.origin)])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Wizard Select Product',
            'res_model': 'select.notice.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('eebc_notices.wizard_select_notice_view').id,  # Aquí se especifica el ID correcto de la vista
            'target': 'new',
            'context': {
                'product_id': self.product_id.id,  # Pasar valores por defecto
                'cantidad':  self.product_uom_qty,
                'location_id': self.picking_id.location_id.id,
                'stock_move_id': self.id,
                'lines':notice_lines_to_wizard,
                'purchase_order_id': order.id

            }
        }

    def _create_line_ids(self):
        for move in self:
            _logger.warning('id del producto :%s',move.product_id.id)
            _logger.warning('id del location_id :%s',move.location_id.id)
            _logger.warning('id del move :%s',move.id)


            if not move.id:
                _logger.warning('entra if')

                continue  # No asignar nada si no hay stock_move_id

            notice_history_ids = self.env['notices.history'].search([
                ('quantity', '>', 0),
                ('product_id', '=', move.product_id.id),
                ('location_id', '=', move.location_id.id)
            ])
            notice_ids = self.env['notices.notices'].search([('history_ids', 'in', notice_history_ids.ids)])
            lines = [(0,0,{'notice_id':notice.id,'quantity': 0}) for notice in notice_ids]
            return lines

           


