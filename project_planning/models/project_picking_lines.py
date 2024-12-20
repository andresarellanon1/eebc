from odoo import fields, models, api

class ProjectPlanPickingLine(models.Model):
    _name = 'project.picking.lines'
    _description = 'Project picking lines'

    name = fields.Char(required=True, string="Nombre")
    
    project_id = fields.Many2one('project.project', string="Proyecto")
    picking_id = fields.Many2one('project.plan.pickings', string="Plantilla de proyecto")
    product_id = fields.Many2one('product.product', string="Producto")
    sale_order_id = fields.Many2one('sale.order')
    
   
    quantity = fields.Float(string="Cantidad")
    location_id = fields.Many2one('stock.location', string="Localización")
    reservado = fields.Float(string='Reservado')
    
   
    picking_name = fields.Char(string="Inventario")
    project_plan_id = fields.Many2one('project.plan', string="Plantilla de tareas")
    stock_move_id = fields.Many2one('stock.move', string='Inventario')
    
    standard_price = fields.Float(string="Precio", compute='_compute_standard_price')
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
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

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id
            self.name = self.product_id.name

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