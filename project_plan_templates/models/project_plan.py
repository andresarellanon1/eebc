from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProjectPlan(models.Model):
    _name = 'project.plan'
    _description = 'Templates for project plans'

    name = fields.Char(string="Nombre", required=True)
    project_name = fields.Char(string="Project name")
    description = fields.Html(string="Descripción")
    note = fields.Char()

    project_plan_lines = fields.One2many('project.plan.line', 'project_plan_id', string="Project plan lines")
    project_id = fields.Many2one('project.project', string="Proyecto")
    project_plan_pickings = fields.Many2many('project.plan.pickings', string="Movimientos de inventario")
    picking_lines = fields.One2many(
        'project.picking.lines',
        'project_plan_id',
        compute="_compute_picking_lines",
        string="Picking Lines",
        store=True
    )

    task_time_lines = fields.One2many('task.time.lines',
        'project_plan_id',
        string="Mano de obra",
        compute="_compute_task_lines",
        store = True
        )

    material_total_cost = fields.Float(string="Costo total", compute="_compute_total_cost", default=0.0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    product_template_id = fields.Many2one(
        'product.template',
        string="Servicio",
        ondelete='restrict',
    )

    service_project_domain = fields.Many2many('product.template', store=True, compute="_compute_service_project_domain")

    labour_total_cost = fields.Float(string="Costo mano de obra", compute="_compute_labour_cost", default=0.0)

    project_plan_pickings = fields.Many2one('project.plan.pickings', string="Lista de materiales")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")

    @api.depends('picking_lines.subtotal')
    def _compute_total_cost(self):
        """
        Calcula el costo total de los materiales basado en las líneas de picking.
        También actualiza el precio de lista del producto asociado.
        """
        for plan in self:
            plan.material_total_cost = sum(line.subtotal for line in plan.picking_lines)  # Suma los subtotales de las líneas de picking
            self.update_product_template_list_price(plan)  # Actualiza el precio de lista del producto


    @api.depends('task_time_lines.price_subtotal')
    def _compute_labour_cost(self):
        """
        Calcula el costo total de la mano de obra basado en las líneas de tareas.
        También actualiza el precio de lista del producto asociado.
        """
        for task in self:
            task.labour_total_cost = sum(line.price_subtotal for line in task.task_time_lines)  # Suma los subtotales de las líneas de tareas
            self.update_product_template_list_price(task)  # Actualiza el precio de lista del producto


    @api.depends('project_plan_pickings')
    def _compute_picking_lines(self):
        """
        Calcula y actualiza las líneas de picking basadas en las plantillas de movimientos.
        """
        for record in self:
            record.picking_lines = [(5, 0, 0)]  # Limpia las líneas existentes
            record.picking_lines = record.get_picking_lines(record.project_plan_pickings)  # Obtiene las nuevas líneas de picking


    @api.depends('task_timesheet_id')
    def _compute_task_lines(self):
        """
        Calcula y actualiza las líneas de tareas basadas en la plantilla de Mano de obra.
        """
        for record in self:
            record.task_time_lines = [(5, 0, 0)]  # Limpia las líneas existentes
            record.task_time_lines = record.get_task_time_lines(record.task_timesheet_id)  # Obtiene las nuevas líneas de tareas


    def get_picking_lines(self, line):
        """
        Obtiene las líneas de picking a partir de las plantillas de movimientos.
        
        :param line: Plantillas de movimientos.
        :return: Lista de líneas de picking.
        """
        picking_lines = []
        for picking in line:
            picking_lines += self.prep_picking_lines(picking)  # Prepara las líneas de picking
        return picking_lines


    def get_task_time_lines(self, line):
        """
        Obtiene las líneas de tareas a partir de la plantilla de Mano de obra.
        
        :param line: Plantilla de Mano de obra.
        :return: Lista de líneas de tareas.
        """
        task_lines = []
        for task in line:
            task_lines += self.prep_task_time_lines(task)  # Prepara las líneas de tareas
        return task_lines


    def prep_picking_lines(self, line):
        """
        Prepara las líneas de picking individuales.
        
        :param line: Línea de la plantilla de movimientos.
        :return: Lista de líneas de picking preparadas.
        """
        picking_lines = []
        for picking in line.project_picking_lines:
            picking_lines.append((0, 0, {
                'name': picking.product_id.name,
                'product_id': picking.product_id.id,
                'product_uom': picking.product_uom.id,
                'product_packaging_id': picking.product_packaging_id.id,
                'product_uom_qty': picking.product_uom_qty,
                'quantity': picking.quantity,
                'standard_price': picking.standard_price,
                'subtotal': picking.subtotal,
                'display_type': False
            }))
        return picking_lines


    def prep_task_time_lines(self, line):
        """
        Prepara las líneas de tareas individuales.
        
        :param line: Línea de la plantilla de Mano de obra.
        :return: Lista de líneas de tareas preparadas.
        """
        task_lines = []
        for task in line.task_time_lines:
            task_lines.append((0, 0, {
                'product_id': task.product_id.id,
                'description': task.description,
                'estimated_time': task.estimated_time,
                'work_shift': task.work_shift,
                'unit_price': task.unit_price,
                'price_subtotal': task.price_subtotal
            }))
        return task_lines


    def prep_picking_section_line(self, line):
        """
        Prepara una línea de sección para las líneas de picking.
        
        :param line: Línea de la plantilla de movimientos.
        :return: Línea de sección preparada.
        """
        return (0, 0, {
            'name': line.name,
            'display_type': line.display_type or 'line_section',
            'product_id': False,
            'product_uom': False,
            'product_packaging_id': False,
            'product_uom_qty': False,
            'quantity': False,
            'standard_price': False,
            'subtotal': False
        })


    def update_product_template_list_price(self, plan):
        """
        Actualiza el precio de lista del producto asociado con el costo total de materiales y mano de obra.
        
        :param plan: Plan de proyecto.
        """
        if plan.product_template_id:
            total_cost = plan.material_total_cost + plan.labour_total_cost  # Calcula el costo total
            plan.product_template_id.write({'list_price': total_cost})  # Actualiza el precio de lista


    @api.model
    def write(self, vals):
        """
        Sobrescribe el método write para actualizar el proyecto asociado al producto.
        """
        result = super(ProjectPlan, self).write(vals)
        if 'product_template_id' in vals and vals['product_template_id']:
            product_template = self.env['product.template'].browse(vals['product_template_id'])
            if product_template and product_template.project_plan_id != self:
                product_template.write({'project_plan_id': self.id})  # Asocia el plan al producto
        return result


    def ensure_plan_line_exists(self):
        """
        Garantiza que exista una línea en project_plan_lines con la información obligatoria.
        Si no existe, crea una nueva línea.
        """
        for plan in self:
            if self.env.context.get('skip_ensure_plan_line_exists'):
                return

            existing_line = self.env['project.plan.line'].search([
                ('project_plan_id', '=', plan.id),
                ('name', '=', plan.name)
            ], limit=1)

            if not existing_line:
                plan.with_context(skip_ensure_plan_line_exists=True).write({
                    'project_plan_lines': [(0, 0, {
                        'name': plan.name,
                        'description': plan.description,
                        'project_plan_pickings': plan.project_plan_pickings.id,
                        'task_timesheet_id': plan.task_timesheet_id.id,
                    })]
            })


    def create(self, vals):
        """
        Sobrescribe el método create para garantizar la existencia de la línea en project_plan_lines.
        """
        record = super(ProjectPlan, self).create(vals)
        record.ensure_plan_line_exists()  # Asegura que exista la línea
        return record


    def write(self, vals):
        """
        Sobrescribe el método write para verificar y crear la línea si no existe.
        """
        result = super(ProjectPlan, self).write(vals)
        self.with_context(skip_ensure_plan_line_exists=True).ensure_plan_line_exists()  # Usa contexto para evitar bucle
        return result