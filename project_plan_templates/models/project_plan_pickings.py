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
    quantity = fields.Float(string="Quantity", required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    reservado = fields.Float(string='Reservado')
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    standard_price = fields.Float(string="Price")
    subtotal = fields.Float(string="Subtotal")
    total_cost = fields.Float(string="Total cost")
    
    def reservado_update(self, task_inventory_lines):
        for record in self:
            for inventory_lines in task_inventory_lines: # Iteramos sobre los movimientos solo una vez por cada registro
                _logger.warning(f'Se itera sobre los productos')
                if record.product_id.id == inventory_lines.product_id.id:  # Verificamos si el producto coincide.
                    _logger.warning(f'Coincidio el producto: {record.product_id.name} con {inventory_lines.product_id.name}')
                    if record.quantity >= (record.reservado + inventory_lines.quantity):
                        record.reservado += inventory_lines.quantity  # Actualizamos el campo 'reservado' sumando la cantidad del stock_move
                        _logger.warning(f'Se actualizo el campo reservado a: {record.reservado}')
        


    @api.onchange('product_id')
    def onchange_product_price(self):
        self.standard_price = self.product_id.standard_price

    @api.onchange('quantity')
    def onchange_quantity(self):
        quantity = self.quantity

        if quantity >= 0:
            self.subtotal = self.standard_price * quantity
        else:
            self.subtotal = 0.00

        self.project_plan_id.calculate_project_plan_cost()