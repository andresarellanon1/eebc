from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectPlanPickings(models.Model):
    _name = 'project.plan.pickings'
    _description = 'Project plan pickings'

    
    name = fields.Char(string="Nombre")
    description = fields.Html(string="Descripción")
    creation_date = fields.Date(string="Creado el", default=fields.Date.context_today, readonly=True)
    creator_id = fields.Many2one('res.users', string="Creado por", default=lambda self: self.env.user)
    
    
    project_picking_lines = fields.One2many('project.picking.lines', 'picking_id', string="Productos")
    
    active = fields.Boolean(string="Activo", default=True)
    project_id = fields.Many2one('project.project', string="Proyecto")

    plan_total_cost = fields.Float(string="Costo total", compute="_compute_total_cost", default=0.0)

    def toggle_active(self):
        for record in self:
            record.active = not record.active

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)
        
    @api.constrains('project_picking_lines')
    def _check_picking_lines(self):
        for record in self:
            if not record.project_picking_lines:
                raise ValidationError("Debe agregar al menos una línea en la pestaña 'Pickings'.")


class ProjectPlanPickingLine(models.Model):
    _name = 'project.picking.lines'
    _description = 'Project picking lines'
    _order = 'sequence'

    name = fields.Char(string="Nombre")
    
    project_id = fields.Many2one('project.project', string="Proyecto")
    picking_id = fields.Many2one('project.plan.pickings', string="Plantilla de proyecto")
    product_id = fields.Many2one('product.product', string="Producto")
    sale_order_id = fields.Many2one('sale.order')
    task_id = fields.Many2one('project.task', string="Tarea")

    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_picking_id')
    
   
    quantity = fields.Float(string="Cantidad")
    location_id = fields.Many2one('stock.location', string="Localización")
    used_quantity = fields.Float(string="Cantidad utilizada", default=0)
    reservado = fields.Float(string='Reservado')
    
   
    picking_name = fields.Char(string="Inventario")
    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas")
    stock_move_id = fields.Many2one('stock.move', string='Movimiento de inventario')
    
    standard_price = fields.Float(string="Precio", compute="_compute_standard_price", store=True)
    last_price = fields.Float(string="Ultimo precio")
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal')
    total_cost = fields.Float(string="Costo total")

    display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    sequence = fields.Integer()
    product_packaging_id = fields.Many2one('product.packaging', 'Empaquetado', domain="[('product_id', '=', product_id)]", check_company=True)
    product_uom = fields.Many2one('uom.uom', string='Unidad de medida')
    company_id = fields.Many2one('res.company', string="Empresa")
    product_uom_qty = fields.Float(string="Demanda")
    for_create = fields.Boolean(default=True)
    for_modification = fields.Boolean(default=True)
    for_newlines = fields.Boolean(default=True)
    not_modificable = fields.Boolean(default=False)

    @api.onchange('used_quantity')
    def _check_quantity(self):
        """
        Valida que la cantidad utilizada no exceda la cantidad disponible.
        Si la cantidad utilizada es mayor que la cantidad disponible, se lanza una excepción.
        """
        for record in self:
            if record.used_quantity > record.quantity:  # Corregido: Se usa `record.quantity` en lugar de `quantity`
                raise ValidationError("Cantidad excedida, ordene más o ingrese la cantidad correcta")


    @api.depends('product_id', 'product_id.standard_price')
    def _compute_standard_price(self):
        """
        Calcula el precio estándar del producto basado en el campo 'standard_price' del producto seleccionado.
        Este método se ejecuta automáticamente cuando cambia el campo 'product_id' o su precio estándar.
        Si el registro no está asociado a una orden de venta o es una nueva línea, se usa el precio estándar del producto.
        """
        for record in self:
            if not record.sale_order_id or record.for_newlines:
                record.standard_price = record.product_id.standard_price
                record.last_price = record.product_id.standard_price  # Actualiza el último precio


    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Actualiza la unidad de medida y el nombre del producto cuando se selecciona un producto.
        Este método se ejecuta automáticamente cuando cambia el campo 'product_id'.
        """
        if self.product_id:
            self.product_uom = self.product_id.uom_id  # Asigna la unidad de medida del producto
            self.name = self.product_id.name  # Asigna el nombre del producto


    def reservado_update(self, task_inventory_lines):
        """
        Actualiza la cantidad reservada del producto en función de las líneas de inventario de la tarea.
        Este método compara el producto actual con las líneas de inventario y actualiza la cantidad reservada.
        
        :param task_inventory_lines: Líneas de inventario de la tarea.
        """
        for record in self:
            for inventory_lines in task_inventory_lines:
                if record.product_id.id == inventory_lines.product_id.id:
                    if record.quantity >= (record.reservado + inventory_lines.quantity):
                        record.reservado += inventory_lines.quantity  # Incrementa la cantidad reservada


    @api.depends('quantity')
    def _compute_subtotal(self):
        """
        Calcula el subtotal multiplicando el precio estándar o el último precio por la cantidad.
        Este método se ejecuta automáticamente cuando cambia el campo 'quantity'.
        Si la cantidad es negativa, el subtotal se establece en 0.00.

        Ademas actualiza el precio unitario de la línea en la orden de venta.
        deacuerdo a los pickings agregados que no pertenezcan a la plantilla.
        """
        for record in self:
            quantity = record.quantity

            if quantity >= 0:
                if record.standard_price > 0:
                    record.subtotal = record.standard_price * quantity  # Usa el precio estándar
                else:
                    record.subtotal = record.last_price * quantity  # Usa el último precio si no hay precio estándar
            else:
                record.subtotal = 0.00  # Si la cantidad es negativa, el subtotal es 0.00

        picking_lines = self.sale_order_id.project_picking_lines
        order_lines = self.sale_order_id.order_line

        new_price = 0

        for line in order_lines:
            
            if line.product_template_id.is_extra:

                for material in picking_lines:

                    if material.for_modification:
                        product = line.product_id
                        new_price = product.list_price + (material.subtotal if material.subtotal else 0)
                        product.write({'list_price': new_price})
                        _logger.warning('Precio de extras: %s', product.list_price)
        
        