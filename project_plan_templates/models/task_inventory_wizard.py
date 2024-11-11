from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class TaskInventoryWizard(models.TransientModel):
    _name = 'task.inventory.wizard'
    _description = 'Wizard to create stock move with selected products'

    # Relación con los productos seleccionados en vez de stock.moves
    product_ids = fields.Many2many('product.product', string="Productos")
    project_task_id = fields.Many2one('project.task', string="Project Task")

    name = fields.Char(string='Referencia')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    picking_type_id = fields.Many2one('stock.picking.type', string="Tipo de operación", compute='_compute_picking_type_id', store=True)
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen', compute="_compute_origin", store=True)
    user_id = fields.Many2one('res.users', string='Usuario')
    company_id = fields.Many2one('res.company', string="Empresa")
    task_id = fields.Many2one('stock.picking', string='Tarea de origen')
    product_packaging_id = fields.Many2one('product.packaging', 'Packaging', domain="[('product_id', '=', product_id)]", check_company=True)

    # Información adicional
    carrier_id = fields.Many2one('delivery.carrier')
    carrier_tracking_ref = fields.Char(string="Referencia de rastreo")
    weight = fields.Float(string="Peso")
    shipping_weight = fields.Float(string="Peso para envío")
    group_id = fields.Many2one('procurement.group', string="Grupo de aprovisionamiento")
    transport_type = fields.Selection(
        string="Tipo de transporte",
        selection=[('00', 'No usa carreteras federales'), ('01', 'Autotransporte Federal')]
    )

    lat_origin = fields.Float(string="Latitud de origen")
    long_origin = fields.Float(string="Longitud de origen")
    lat_dest = fields.Float(string="Latitud de destino")
    long_dest = fields.Float(string="Longitud de destino")
    custom_document_identification = fields.Char(string="Customs Document Identification")

    @api.model
    def _compute_fields(self):
        for record in self:
            record.task_id = record.project_task_id.id

    @api.onchange('name')
    def _compute_origin(self):
        # Aquí podrías realizar cualquier cálculo para obtener el origen basado en el nombre
        self.origin = self.name

    @api.onchange('name')
    def _compute_picking_type_id(self):
        if self.project_task_id:
            self.picking_type_id = self.project_task_id.project_id.default_picking_type_id

    def action_confirm_create_inventory(self):
        # Verificar que haya productos seleccionados
        if not self.product_ids:
            raise ValueError("Debe seleccionar al menos un producto.")

        # Crear un solo stock.move con todos los productos
        stock_move_vals = {
            'product_id': False,  # Este campo puede quedarse vacío si solo se trata de un único movimiento
            'product_uom_qty': sum(product.standard_price for product in self.product_ids),  # Cantidad total de todos los productos
            'quantity_done': sum(product.standard_price for product in self.product_ids),  # Este campo es opcional
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'name': self.name,
            'scheduled_date': self.scheduled_date,
            'origin': self.origin,
            'carrier_id': self.carrier_id.id,
            'carrier_tracking_ref': self.carrier_tracking_ref,
            'weight': self.weight,
            'shipping_weight': self.shipping_weight,
            'user_id': self.user_id.id,
            'transport_type': self.transport_type,
            'lat_origin': self.lat_origin,
            'long_origin': self.long_origin,
            'lat_dest': self.lat_dest,
            'long_dest': self.long_dest,
        }

        # Crear un solo Stock Move
        stock_move = self.env['stock.move'].create(stock_move_vals)

        # Crear un picking con este stock move
        stock_picking_vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.origin,
            'move_ids': [(4, stock_move.id)],  # Enlazamos el movimiento creado al picking
            'carrier_id': self.carrier_id.id,
            'carrier_tracking_ref': self.carrier_tracking_ref,
            'weight': self.weight,
            'shipping_weight': self.shipping_weight,
            'user_id': self.user_id.id,
            'transport_type': self.transport_type,
            'lat_origin': self.lat_origin,
            'long_origin': self.long_origin,
            'lat_dest': self.lat_dest,
            'long_dest': self.long_dest,
        }

        stock_picking = self.env['stock.picking'].create(stock_picking_vals)

        self.project_task_id.project_id.project_picking_lines.reservado_update(stock_move_ids)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': stock_picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
