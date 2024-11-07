from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'


# TODO: que picking id sea tipo de entrada para que salga el boton de aviso
# campo que muestre el aviso relacionado


    has_aviso_in_attributes = fields.Boolean(
        string="Tiene 'aviso' en atributos",
        compute='_compute_has_aviso_in_attributes'
    )
    has_aviso_in_attributes_fake = fields.Boolean(
        string="Tiene 'aviso' en atributos",
        compute="_compute_has_aviso_in_attributes"
    )



    has_type_picking_notice_approve= fields.Boolean(
        string="Puede el tipo de operacion crear aviso  ",
        compute='_compute_has_aviso_in_attributes'
    )
    picking_type_codigo = fields.Selection(
        related='picking_type_id.code',
        readonly=True)

    @api.depends('product_id.attribute_line_ids', 'picking_type_id.code')
    def _compute_has_aviso_in_attributes(self):
        for move in self:
            # Verifica si el producto tiene el atributo 'aviso' y si el tipo de picking está relacionado con la orden de compra
            move.has_aviso_in_attributes = (
                any('aviso' in attr.name for attr in move.product_id.attribute_line_ids.mapped('attribute_id')) 
            )
            move.has_type_picking_notice_approve = move.picking_type_id.code == 'incoming'
            _logger.warning("valor de has_aviso_in_attributes %s", move.has_aviso_in_attributes)
            _logger.warning("valor de has_type_picking_notice_approve %s", move.has_type_picking_notice_approve)

            if move.has_aviso_in_attributes ==True and move.has_type_picking_notice_approve==True :
                move.has_aviso_in_attributes_fake = True
                _logger.warning("valor de has_aviso_in_attributes_fake %s", move.has_aviso_in_attributes_fake)

        
        


    
    
    def call_wizard(self):

        _logger.warning('Producto name: %s', self.product_id.name)
        _logger.warning('Cantidad: %s', self.product_uom_qty)
        _logger.warning('type: %s', self.picking_id.picking_type_code)
        
        _logger.warning('Descripcion: %s', self.description_picking)
        

        _logger.warning('documento origen: %s', self.origin)

        # Buscar la orden de compra relacionada con el origen
        order = self.env['purchase.order'].search([('name', '=', self.origin)])

        # Obtener las facturas y sus nombres
        invoice_names = ", ".join(order.invoice_ids.mapped('name')) if order.invoice_ids else "No hay facturas"

        _logger.warning('invoices: %s', invoice_names)

        # Obtener el nombre del proveedor
        proveedor_name = self.picking_id.partner_id.name if self.picking_id.partner_id else "Proveedor no definido"

  
        # Obtener el ID del proveedor
        proveedor_id = self.picking_id.partner_id.id if self.picking_id.partner_id else False
        _logger.warning('Proveedor ID: %s', proveedor_id)

        # Obtener el ID de la orden de compra
        purchase_order_id = order.id if order else False
        _logger.warning('Purchase Order ID: %s', purchase_order_id)
       
        # Obtener la descripción del producto en la línea del picking
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
                'purchase_id': purchase_order_id,
                'date_aprovee': order.date_approve,
                'product_description':product_description,
                'invoices': invoice_names , # Pasar los nombres de las facturas
            }
        }
        
    #    # Aquí el registro 'self' es el stock.move en el que se hizo clic
    #     _logger.warning('Entramos al método de crear aviso para el movimiento: %s', self.id)

    #     # Puedes acceder a los datos de la línea (stock.move) que recibió el clic
    #     _logger.warning('Producto: %s', self.product_id)
    #     _logger.warning('Cantidad: %s', self.product_uom_qty)
    #     _logger.warning('Parner: %s', self.picking_id.partner_id)
        

    #     # Crear el aviso relacionado a partir de los datos del movimiento
    #     notice_vals = {
    #         'description': 'Aviso generado para el producto %s en la operación %s' % (self.product_id.name, self.picking_id.name),
    #         'quantity': self.product_uom_qty,
    #         'resource': self.product_id.id,
    #         'supplier': self.picking_id.partner_id.id,
    #         'description': self.product_id.description,
            
    #         # Otros valores que quieras pasar a notices.notices
    #     }
    #     _logger.warning('VALS PARA AVISO: %s', notice_vals)
        
        
    #     notice = self.env['notices.notices'].create(notice_vals)
    #     _logger.warning('Se ha creado el aviso con ID: %s', notice.id)
        


