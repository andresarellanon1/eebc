from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)

class TaskTimeLines(models.Model):

    _name = 'task.time.lines'
    _description = 'Project plan time lines model'

    name = fields.Char(string="Descripción")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")
    project_plan_id = fields.Many2one('project.plan')

    product_id = fields.Many2one('product.template', string="Mano de obra")
    product_domain = fields.Many2many('product.template', compute="_product_domain", store=True)

    description = fields.Char(string="Descripción")
    estimated_time = fields.Float(string="Horas estimadas", compute="_compute_estimated_hours", store=True)
    work_shift = fields.Float(string='Jornadas Laborales')

    unit_price = fields.Float(string="Precio", default=0.0)
    price_subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", default=0.0)

    sale_order_id = fields.Many2one('sale.order', string="Orden de venta")
    display_type = fields.Selection(
            [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    for_modification = fields.Boolean(default=True)
    not_modificable = fields.Boolean(default=False)

    @api.depends('work_shift')
    def _compute_estimated_hours(self):
        """
        Calcula el tiempo estimado en horas multiplicando el número de turnos (`work_shift`) por 8 horas por turno.
        Este método se ejecuta automáticamente cuando cambia el campo `work_shift`.
        """
        for record in self:
            record.estimated_time = record.work_shift * 8  # 8 horas por turno

    def _product_domain(self):
        """
        Define un dominio para filtrar productos que son mano de obra, están disponibles para venta.
        """
        for record in self:
            products = self.env['product.template'].search([
                ('detailed_type', '=', 'service'),  # Solo servicios
                ('sale_ok', '=', True),  # Disponibles para venta
                ('is_labour', '=', True)  
            ])

            record.product_domain = [(6, 0, products.ids)]
            logger.warning(f"[Productos encontrados: {products.ids}]")

    @api.onchange('product_id')
    def _onchange_product(self):
        """
        Actualiza el precio unitario (`unit_price`) con el precio estándar del producto seleccionado.
        Este método se ejecuta automáticamente cuando cambia el campo `product_id`.
        """
        for record in self:
            record.unit_price = record.product_id.standard_price  # Asignar el precio estándar del producto


    @api.depends('work_shift')
    def _compute_subtotal(self):
        """
        Calcula el subtotal multiplicando el precio unitario (`unit_price`) por el número de turnos (`work_shift`).
        Este método se ejecuta automáticamente cuando cambia el campo `work_shift`.
        Si el número de turnos es negativo, el subtotal se establece en 0.00.
        """
        for record in self:
            quantity = record.work_shift

            if quantity >= 0:
                record.price_subtotal = record.unit_price * quantity  # Calcular el subtotal
            else:
                record.price_subtotal = 0.00  # Si la cantidad es negativa, el subtotal es 0.00