from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ProjectPlanPickings(models.Model):
    _name = 'project.plan.pickings'
    _description = 'Project plan pickings'

    
    name = fields.Char(string="Name")
    description = fields.Html(string="Description")
    creation_date = fields.Date(string="Created on", default=fields.Date.context_today, readonly=True)
    creator_id = fields.Many2one('res.users', string="Created by", default=lambda self: self.env.user)
    
    
    project_picking_lines = fields.One2many('project.picking.lines', 'picking_id', string="Products")
    active = fields.Boolean(string="Active", default=True)
    project_id = fields.Many2one('project.project', string="Project")

    plan_total_cost = fields.Float(string="Total cost",  compute='_compute_total_cost', default=0.0)

    @api.constrains('product_id')
    def _check_product_id(self):
        for record in self:
            if not record.product_id:
                raise ValidationError("El campo 'Product' es obligatorio. No se puede guardar un registro sin este campo.")

    def toggle_active(self):
        for record in self:
            record.active = not record.active

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)


class ProjectPlanPickingLine(models.Model):
    _name = 'project.picking.lines'
    _description = 'Project picking lines'

    name = fields.Char(required=True)
    
    project_id = fields.Many2one('project.project', string="Project Plan")
    picking_id = fields.Many2one('project.plan.pickings', string="Picking Template")
    product_id = fields.Many2one('product.product', string="Product")
    sale_order_id = fields.Many2one('sale.order')
    
   
    quantity = fields.Float(string="Quantity")
    location_id = fields.Many2one('stock.location', string="Location")
    reservado = fields.Float(string='Reservado')
    
   
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    
    standard_price = fields.Float(string="Price", compute='_compute_standard_price')
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    total_cost = fields.Float(string="Total cost")

    display_type = fields.Selection(
        [
            ('line_section', 'Section'),
            ('line_note', 'Note'),
        ]
    )
    sequence = fields.Integer()
    product_packaging_id = fields.Many2one('product.packaging', 'Packaging', domain="[('product_id', '=', product_id)]", check_company=True)
    product_uom = fields.Many2one('uom.uom', string='Unidad de medida')
    company_id = fields.Many2one('res.company', string="Empresa")
    product_uom_qty = fields.Float(string="Demanda")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id

    def reservado_update(self, task_inventory_lines):
        for record in self:
            for inventory_lines in task_inventory_lines:
                if record.product_id.id == inventory_lines.product_id.id:
                    if record.quantity >= (record.reservado + inventory_lines.quantity):
                        record.reservado += inventory_lines.quantity

    @api.depends('product_id')
    def _compute_standard_price(self):
        for record in self:
            record.standard_price = record.product_id.standard_price
            

    @api.depends('quantity')
    def _compute_subtotal(self):
        for record in self:
            quantity = record.quantity

            if quantity >= 0:
                record.subtotal = record.standard_price * quantity
            else:
                record.subtotal = 0.00