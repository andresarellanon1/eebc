from odoo import fields, models, api

class StockMove(models.Model):
   
    _inherit = 'stock.move'

    product_id = fields.Many2one('product.product', string='product', domain="[('id', 'in', 'picking_id.task_id.project_id.project_picking_lines.mapped('product_id').ids')]")

    # stock.move (picking_id) - stock.picking (task_id) - project.task (project_id) - project.project (project_picking_lines) project.project (project_picking_ids)