from odoo import fields, models, api

class TaskTimeLines(models.Model):

    _name = 'task.time.lines'
    _description = 'Project plan time lines model'

    name = fields.Char(string="Descripción")
    task_timesheet_id = fields.Many2one('task.timesheet', string="Hoja de horas")
    project_plan_id = fields.Many2one('project.plan')

    product_id = fields.Many2one('product.template', string="Mano de obra")
    product_domain = fields.Many2many('product.template', store=True)

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

    @api.depends('work_shift')
    def _compute_estimated_hours(self):
        for record in self:
            record.estimated_time = record.work_shift * 8
        
    # def _product_domain(self):
    #     for record in self:
    #         products = self.env['product.template'].search([
    #             ('detailed_type', '=', 'service'), 
    #             ('sale_ok', '=', True),
    #             ('name', '=', 'CUADRILLA INSTALADORA')
    #         ])

    @api.onchange('product_id')
    def _onchange_product(self):
        for record in self:
            record.unit_price = record.product_id.standard_price


    @api.depends('work_shift')
    def _compute_subtotal(self):
        for record in self:
            quantity = record.work_shift

            if quantity >= 0:
                record.price_subtotal = record.unit_price * quantity
            else:
                record.subtotal = 0.00