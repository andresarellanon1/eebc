from odoo import api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)




class StockQuant(models.Model):
    _inherit = 'stock.quant'




    @api.model_create_multi
    def create(self, vals_list):
        """ Override to handle the "inventory mode" and create a quant as
        superuser the conditions are met.
        """
        quants = self.env['stock.quant']
        is_inventory_mode = self._is_inventory_mode()
        allowed_fields = self._get_inventory_fields_create()

        _logger.warning('valor de vals list para crear stock.quant: %s', vals_list)

        for vals in vals_list:
            if is_inventory_mode and any(f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
                if any(field for field in vals.keys() if field not in allowed_fields):
                    raise UserError(_("Quant's creation is restricted, you can't do this operation."))
                auto_apply = 'inventory_quantity_auto_apply' in vals
                inventory_quantity = vals.pop('inventory_quantity_auto_apply', False) or vals.pop(
                    'inventory_quantity', False) or 0
                # Create an empty quant or write on a similar one.
                product = self.env['product.product'].browse(vals['product_id'])
                location = self.env['stock.location'].browse(vals['location_id'])
                lot_id = self.env['stock.lot'].browse(vals.get('lot_id'))
                package_id = self.env['stock.quant.package'].browse(vals.get('package_id'))
                owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
                quant = self.env['stock.quant']
                if not self.env.context.get('import_file'):
                    # Merge quants later, to make sure one line = one record during batch import
                    quant = self._gather(product, location, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                if lot_id:
                    if self.env.context.get('import_file') and lot_id.product_id != product:
                        lot_name = lot_id.name
                        lot_id = self.env['stock.lot'].search([('product_id', '=', product.id), ('name', '=', lot_name)], limit=1)
                        if not lot_id:
                            company_id = location.company_id or self.env.company
                            lot_id = self.env['stock.lot'].create({'name': lot_name, 'product_id': product.id, 'company_id': company_id.id})
                        vals['lot_id'] = lot_id.id
                    quant = quant.filtered(lambda q: q.lot_id)
                if quant:
                    quant = quant[0].sudo()
                else:
                    quant = self.sudo().create(vals)
                    if 'quants_cache' in self.env.context:
                        self.env.context['quants_cache'][
                            quant.product_id.id, quant.location_id.id, quant.lot_id.id, quant.package_id.id, quant.owner_id.id
                        ] |= quant
                if auto_apply:
                    quant.write({'inventory_quantity_auto_apply': inventory_quantity})
                else:
                    # Set the `inventory_quantity` field to create the necessary move.
                    quant.inventory_quantity = inventory_quantity
                    quant.user_id = vals.get('user_id', self.env.user.id)
                    quant.inventory_date = fields.Date.today()
                quants |= quant
            else:
                quant = super().create(vals)
                if 'quants_cache' in self.env.context:
                    self.env.context['quants_cache'][
                        quant.product_id.id, quant.location_id.id, quant.lot_id.id, quant.package_id.id, quant.owner_id.id
                    ] |= quant
                quants |= quant
                if self._is_inventory_mode():
                    quant._check_company()
        return quants




class StockLot(models.Model):
    _inherit = 'stock.lot'



    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('valor de vals list para crear stock.lot: %s', vals_list)

        self._check_create()
        return super(StockLot, self.with_context(mail_create_nosubscribe=True)).create(vals_list)





class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'



    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('valor de vals list para crear stock.move.line: %s', vals_list)

        for vals in vals_list:
            if vals.get('move_id'):
                vals['company_id'] = self.env['stock.move'].browse(vals['move_id']).company_id.id
            elif vals.get('picking_id'):
                vals['company_id'] = self.env['stock.picking'].browse(vals['picking_id']).company_id.id
            if vals.get('move_id') and 'picked' not in vals:
                vals['picked'] = self.env['stock.move'].browse(vals['move_id']).picked
            if vals.get('quant_id'):
                vals.update(self._copy_quant_info(vals))


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

    # agregar campo notices
    
    # notice_established = fields.Boolean(string = 'Aviso establecido', 
    # default=False
    # )
    
    # notice_selected = fields.Boolean(string = 'Aviso seleccionado', 
    # default=False
    # )


    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('valor de vals list para crear stock.move: %s', vals_list)
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
        order = self.env['purchase.order'].search([('name', '=', self.origin)])

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
            # notice_history_ids = self.env['notices.history'].search([
            #     ('product_id', '=', move.product_id.id),
            #     ('location_id', '=', move.location_id.id)
            # ])
            # ('history_ids', 'in', notice_history_ids.ids),
            notice_ids = self.env['notices.notices'].search([('quantity', '>=', 0),('stock_move_id','=', self.id)])
            lines = [(0,0,{'notice_id':notice.id,'quantity': 0, 'quantity_available': notice.quantity,'aviso_name':notice.display_name, 'in_or_out': in_or_out, }) for notice in notice_ids]
            _logger.warning(f'Líneas creadas: {lines}')
            return lines

           


