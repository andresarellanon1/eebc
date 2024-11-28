from odoo import fields, models, api

# Model to manage project plan picking templates. 
# This model stores template configurations for project pickings,
# including product lines and their quantities.
# It tracks creation details and allows templates to be archived through an active flag.
class ProjectPlanPickings(models.Model):
    _name = 'project.plan.pickings'
    _description = 'Project plan pickings'

    # Basic template information fields
    name = fields.Char(string="Name")
    description = fields.Html(string="Description")
    creation_date = fields.Date(string="Created on", default=fields.Date.context_today, readonly=True)
    creator_id = fields.Many2one('res.users', string="Created by", default=lambda self: self.env.user)
    
    # Relations and configuration fields
    project_picking_lines = fields.One2many('project.picking.lines', 'picking_id', string="Products")
    active = fields.Boolean(string="Active", default=True)
    project_id = fields.Many2one('project.project', string="Project")

    plan_total_cost = fields.Float(string="Total cost",  compute='_compute_total_cost', default=0.0)

    # Override of create method to handle any additional 
    # logic needed during template creation.
    @api.model
    def create(self, vals):
        record = super(ProjectPlanPickings, self).create(vals)
        return record

    # Toggles the active state of the template, allowing
    # templates to be archived or unarchived.
    def toggle_active(self):
        for record in self:
            record.active = not record.active

    @api.depends('project_picking_lines.subtotal')
    def _compute_total_cost(self):
        for plan in self:
            plan.plan_total_cost = sum(line.subtotal for line in plan.project_picking_lines)

# Model to manage individual product lines within
# project plan picking templates. Handles product 
# quantities, locations, and computed costs for project materials.
class ProjectPlanPickingLine(models.Model):
    _name = 'project.picking.lines'
    _description = 'Project picking lines'

    name = fields.Char()
    # Relation fields for project and template linking
    project_id = fields.Many2one('project.project', string="Project Plan")
    picking_id = fields.Many2one('project.plan.pickings', string="Picking Template")
    product_id = fields.Many2one('product.product', string="Product")
    sale_order_id = fields.Many2one('sale.order')
    
    # Quantity and location tracking fields
    quantity = fields.Float(string="Quantity")
    location_id = fields.Many2one('stock.location', string="Location")
    reservado = fields.Float(string='Reservado')
    
    # Additional reference and linking fields
    picking_name = fields.Char(string="Picking Name")
    project_plan_id = fields.Many2one('project.plan', string="Project plan")
    stock_move_id = fields.Many2one('stock.move', string='Project Stock')
    
    # Computed cost fields
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
    
    # Updates the reserved quantity for products based on
    # task inventory lines. Verifies that the requested 
    # reservation quantity doesn't exceed the available 
    # quantity and updates the reserved amount accordingly.
    def reservado_update(self, task_inventory_lines):
        for record in self:
            for inventory_lines in task_inventory_lines:
                if record.product_id.id == inventory_lines.product_id.id:
                    if record.quantity >= (record.reservado + inventory_lines.quantity):
                        record.reservado += inventory_lines.quantity

    # Computes the standard price for each product line 
    # by fetching the current standard price from the product.
    @api.depends('product_id')
    def _compute_standard_price(self):
        for record in self:
            record.standard_price = record.product_id.standard_price

    # Computes the subtotal cost for each line
    # by multiplying the standard price with the quantity. 
    # Returns 0.00 for negative quantities.
    @api.depends('quantity')
    def _compute_subtotal(self):
        for record in self:
            quantity = record.quantity

            if quantity >= 0:
                record.subtotal = record.standard_price * quantity
            else:
                record.subtotal = 0.00