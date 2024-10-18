from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    quantity = fields.Integer(string='Cantidad')
    reserved_qty = fields.Float(string='Reservado')
    total_cost = fields.Float(string='Costo total', compute="_compute_total_cost", store=True)
    
    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto',
        store = True,
        copied = True
    )

    product_id = fields.Many2one(
        'product.product', 
        string='Producto',
        store = True,
        copied = True
    )

    @api.onchange('product_id')
    def _onchange_activities_tmpl_id(self):
        for record in self:
            record.name = record.product_id.name
            record.standard_price = record.product_tmpl_id.standard_price

    @api.onchange('quantity')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.product_id.lst_price * record.quantity
