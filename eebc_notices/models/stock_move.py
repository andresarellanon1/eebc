from odoo import api, fields, models
import logging
from odoo.exceptions import UserError

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
    def _generate_serial_numbers(self, next_serial, next_serial_count=False, location_id=False):
        self.ensure_one()
        if not location_id:
            location_id = self.location_dest_id

        if self.product_id.is_aviso:  # Ahora se utiliza el campo is_aviso correctamente
            # Validar que los números de serie no existan
            existing_lots = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id),
            ]).mapped('name')

            lot_names = self.env['stock.lot'].generate_lot_names(next_serial, next_serial_count or self.next_serial_count)
            for lot in lot_names:
                if lot['lot_name'] in existing_lots:
                    raise ValidationError(_(
                        "El número de serie/lote '%s' ya existe para el producto '%s'."
                    ) % (lot['lot_name'], self.product_id.display_name))

        # Continuar con la generación normal de números de serie
        lot_names = self.env['stock.lot'].generate_lot_names(next_serial, next_serial_count or self.next_serial_count)
        field_data = [{'lot_name': lot_name['lot_name'], 'quantity': 1} for lot_name in lot_names]
        move_lines_commands = self._generate_serial_move_line_commands(field_data)
        self.move_line_ids = move_lines_commands
        return True
        

    def _create_lot_ids_from_move_line_vals(self, vals_list, product_id, company_id):
        _logger.warning("Entramos a _create_lot_ids_from_move_line_vals ")
        # Obtener los nombres de los lotes que ya existen
        existing_lots = self.env['stock.lot'].search([
            ('product_id', '=', product_id),
            ('company_id', '=', company_id),
        ]).mapped('name')

        # Filtrar y crear solo los lotes que no existen
        lot_names = {vals['lot_name'] for vals in vals_list if vals.get('lot_name')}
        new_lots = lot_names - set(existing_lots)
        lots_to_create_vals = [
            {'product_id': product_id, 'name': lot_name, 'company_id': company_id}
            for lot_name in new_lots
        ]

        # Crear los nuevos lotes
        lot_ids = self.env['stock.lot'].create(lots_to_create_vals)
        lot_id_by_name = {lot.name: lot.id for lot in lot_ids}

        # Asignar lot_id a los valores de las líneas de movimiento
        for vals in vals_list:
            if vals.get('lot_name') in lot_id_by_name:
                vals['lot_id'] = lot_id_by_name[vals['lot_name']]
                vals['lot_name'] = False



    def action_assign_serial(self):
        _logger.warning('Estamos en el action_assign_serial heredado')

        has_aviso = any('aviso' in attr.name for attr in self.product_id.attribute_line_ids.mapped('attribute_id'))

        _logger.warning('valor de has_aviso en action_assign_serial: %s', has_aviso)
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.act_assign_serial_numbers")
        action['context'] = {
            'default_product_id': self.product_id.id,
            'default_move_id': self.id,
            'is_aviso': has_aviso
        }
        return action


    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('valor de vals list para crear stock.move: %s', vals_list)
        # se debe validar que en una entrada de un producto con aviso pida forzosamente el registrar aviso

        for vals in vals_list:
            if (vals.get('quantity') or vals.get('move_line_ids')) and 'lot_ids' in vals:
                vals.pop('lot_ids')
            picking_id = self.env['stock.picking'].browse(vals.get('picking_id'))
            if picking_id.group_id and 'group_id' not in vals:
                vals['group_id'] = picking_id.group_id.id
            if vals.get('state') == 'done':
                vals['picked'] = True
        res = super().create(vals_list)
        res._update_orderpoints()
        return res

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
        in_or_out = "in"
        notice_lines_to_wizard =self._create_line_ids(in_or_out)
        # aqui va variable para saber que haremos entrada y pasarla a la llave in_or_out
        _logger.warning('LOTES: %s', self.lot_ids)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Wizard File Upload',
            'res_model': 'notice.file.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('eebc_notices.wizard_notice_file_view').id,  # Aquí se especifica el ID correcto de la vista
            'target': 'new',
            'context': {
                'stock_move_id': self.id,
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
                'lines':notice_lines_to_wizard,
                
            }
        }
        
    def action_show_outgoing(self):
        in_or_out = "out"
        notice_lines_to_wizard =self._create_line_ids(in_or_out)
        _logger.warning('1')
        order = self.env['purchase.order'].search([('name', '=', self.origin)])
        _logger.warning('2')


        # aqui va variable para saber que haremos salida y pasarla a la llave in_or_out

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
                'purchase_order_id': order.id,

            }
        }




    def _create_line_ids(self, in_or_out):
        for move in self:
            if not move.id:
                continue 
           
            notice_ids = self.env['notices.notices'].search([('product_id', '=', self.product_id.id),('quantity', '>=', 0)])

            lines = []

            for notice in notice_ids:
                lot_line_ids = []
                _logger.warning(f'Valor de lot_ids {notice.lot_ids} del notices {notice.display_name}')
                if in_or_out == "out":
                    lot_line_ids = [
                        (0, 0, {
                            'lot_id': lot.id,
                            'quantity': 0,
                        }) for lot in notice.lot_ids
                    ]
                lines.append((0, 0, {
                    'notice_id': notice.id,
                    'quantity': 0,
                    'quantity_available': notice.quantity,
                    'aviso_name': notice.display_name,
                    'in_or_out': in_or_out,
                    'lot_line_ids': lot_line_ids if in_or_out == "out" else  '',
                }))
            _logger.warning(f'Líneas creadas: {lines}')
            return lines

           


