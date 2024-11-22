from odoo import fields, models, api

class ProjectPickingWizardLine(models.TransientModel):
    _name = 'project.picking.wizard.line'
    _description = 'Porject picking wizard lines'

    wizard_creation_id = fields.Many2one('project.creation.wizard')

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    reservado = fields.Float(string='Reservado')
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    standard_price = fields.Float(string="Price", compute='_compute_standard_price')
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    total_cost = fields.Float(string="Total cost")

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