from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

class ProjectCreation(models.TransientModel):
    _name = 'task.inventory.wizard'
    _description = 'Wizard to confirm project creation'

    project_task_id = fields.Many2one('project.task', string="Project Task")
    project_stock_products = fields.Many2many('product.product', string="Productos")
    task_inventory_lines = fields.One2many('task.inventory.line', 'inventory_id', string='Productos del proyecto')
    
    name = fields.Char(string='Referencia')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    picking_type_id = fields.Many2one('stock.picking.type', string='Tipo de operación', compute='_compute_picking_type_id')
    location_id = fields.Many2one('stock.location', string='Ubicación de origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de destino')
    scheduled_date = fields.Datetime(string='Fecha programada')
    origin = fields.Char(string='Documento origen', compute="_compute_origin")
    task_id = fields.Many2one('stock.picking', string='Tarea de origen')
    task_id_char = fields.Char(string='Tarea origen', compute="_compute_task_id")
    user_id = fields.Many2one('res.users', string='Usuario')
    product_packaging_id = fields.Many2one('product.packaging', 'Packaging', domain="[('product_id', '=', product_id)]", check_company=True)
    note = fields.Text(string="Note")

    carrier_id = fields.Many2one('delivery.carrier')
    carrier_tracking_ref = fields.Char(string="Referencia de rastreo")
    weight = fields.Float(string="Peso")
    shipping_weight = fields.Float(string="Peso para envío")
    group_id = fields.Many2one('procurement.group', string="Grupo de aprovisionamiento")
    company_id = fields.Many2one('res.company', string="Empresa")
    transport_type = fields.Selection(string="Tipo de transporte", selection=[('00', 'No usa carreteras federales'), ('01', 'Autotransporte Federal')])
    custom_document_identification = fields.Char(string="Customs Document Identification")

    lat_origin = fields.Float(string="Latitud de origen")
    long_origin = fields.Float(string="Longitud de origen")
    lat_dest = fields.Float(string="Latitud de destino")
    long_dest = fields.Float(string="Longitud de destino")

    @api.onchange('name')
    def _compute_task_id(self):
        """
        Actualiza el campo `task_id_char` con el nombre de la tarea asociada (`project_task_id`).
        Este método se ejecuta cuando cambia el campo `name`.
        """
        self.task_id_char = self.project_task_id.name


    @api.onchange('name')
    def _compute_picking_type_id(self):
        """
        Actualiza el campo `picking_type_id` con el tipo de operación predeterminado del proyecto asociado.
        Este método se ejecuta cuando cambia el campo `name`.
        """
        self.picking_type_id = self.project_task_id.project_id.default_picking_type_id.id


    @api.onchange('name')
    def _compute_origin(self):
        """
        Actualiza el campo `origin` con el nombre de la tarea asociada (`project_task_id`).
        Este método se ejecuta cuando cambia el campo `name`.
        """
        self.origin = self.project_task_id.name


    @api.onchange('name')
    def _onchange_project_task_id(self):
        """
        Actualiza los productos disponibles en el campo `product_id` basados en los productos asociados
        a las líneas de picking del proyecto. También establece el dominio para `product_id`.
        Este método se ejecuta cuando cambia el campo `name`.
        """
        if self.project_task_id:
            project = self.project_task_id.project_id
            # Obtener los IDs de los productos asociados a las líneas de picking del proyecto
            product_ids = [int(product.id) for product in project.project_picking_lines.mapped('product_id')]
            # Asignar los productos al campo `project_stock_products`
            self.project_stock_products = [(6, 0, product_ids)]
            # Establecer el dominio para `product_id`
            return {'domain': {'product_id': [('id', 'in', product_ids)]}}


    @api.onchange('task_inventory_lines')
    def _compute_max_quantity(self):
        """
        Calcula la cantidad máxima disponible para cada producto en las líneas de inventario de la tarea.
        Este método se ejecuta cuando cambia el campo `task_inventory_lines`.
        """
        for inv_lines in self.task_inventory_lines:
            for proyect_lines in self.project_task_id.project_id.project_picking_lines:
                if inv_lines.product_id == proyect_lines.product_id:
                    # Calcular la cantidad máxima disponible
                    inv_lines.max_quantity = proyect_lines.quantity - proyect_lines.reservado


    def _quantity_flag(self):
        """
        Verifica si alguna línea de inventario excede la cantidad máxima disponible.
        
        :return: True si alguna línea excede la cantidad máxima, False en caso contrario.
        """
        for inv_lines in self.task_inventory_lines:
            for proyect_lines in self.project_task_id.project_id.project_picking_lines:
                if inv_lines.product_id == proyect_lines.product_id:
                    if inv_lines.quantity > inv_lines.max_quantity:
                        return True
        return False


    def action_confirm_create_inventory(self):
        """
        Confirma la creación del inventario y genera un movimiento de stock.
        Si alguna línea de inventario excede la cantidad máxima, se lanza una excepción.
        """
        self.ensure_one()

        if self._quantity_flag():
            raise ValidationError("La cantidad de los productos no puede ser mayor a la cantidad máxima")
        else:
            # Actualizar la cantidad reservada en las líneas de picking del proyecto
            self.project_task_id.project_id.project_picking_lines.reservado_update(self.task_inventory_lines)

            # Preparar los valores para los movimientos de stock
            stock_move_ids_vals = [(0, 0, {
                'product_id': line.product_id.id,
                'product_packaging_id': line.product_packaging_id.id,
                'product_uom_qty': line.product_uom_qty,
                'quantity': line.quantity,
                'product_uom': line.product_uom.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'name': self.name,
            }) for line in self.task_inventory_lines]

            # Preparar los valores para el picking de stock
            stock_picking_vals = {
                'name': self.name,
                'partner_id': self.partner_id.id,
                'picking_type_id': self.project_task_id.project_id.default_picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'scheduled_date': self.scheduled_date,
                'origin': self.project_task_id.name,
                'task_id': self.project_task_id.id,
                'user_id': self.user_id.id,
                'move_ids': stock_move_ids_vals,
                'carrier_id': self.carrier_id.id,
                'carrier_tracking_ref': self.carrier_tracking_ref,
                'weight': self.weight,
                'shipping_weight': self.shipping_weight,
                'group_id': self.group_id.id,
                'company_id': self.company_id.id,
                'transport_type': self.transport_type,
                'custom_document_identification': self.custom_document_identification,
                'lat_origin': self.lat_origin,
                'long_origin': self.long_origin,
                'lat_dest': self.lat_dest,
                'long_dest': self.long_dest,
                'note': self.note,
            }

            # Crear el picking de stock
            stock_picking = self.env['stock.picking'].create(stock_picking_vals)

            # Abrir la vista del picking creado
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'res_id': stock_picking.id,
                'view_mode': 'form',
                'target': 'current',
            }
        