from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


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

    @api.model
    def create(self, vals):
        record = super(ProjectPlanPickings, self).create(vals)
        return record

    def toggle_active(self):
        for record in self:
            record.active = not record.active

class ProjectPlanPickingLine(models.Model):
    _name = 'project.picking.lines'
    _description = 'Project picking lines'


    project_id = fields.Many2one('project.project', string="Project Plan")
    picking_id = fields.Many2one('project.plan.pickings', string="Picking Template")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", compute="_compute_subtotal", required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    reservado = fields.Float(string='Reservado')
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    standard_price = fields.Float(string="Price", compute='_compute_standard_price')
    subtotal = fields.Float(string="Subtotal")
    total_cost = fields.Float(string="Total cost")
    
    def reservado_update(self, task_inventory_lines):
        for record in self:
            for move_id in move_ids: # Iteramos sobre los movimientos solo una vez por cada registro.
                if record.product_id == move_id.product_id:  # Verificamos si el producto coincide.
                    record.reservado += move_id.quantity  # Actualizamos el campo 'reservado' sumando la cantidad del stock_move

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