from odoo import models, fields, api

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    picking_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    product_ids = fields.One2many('product.product', 'project_id', string='Products')

    @api.depends('task_id.stock_ids')
    def _compute_pickin_ids(self):
        for record in self:
            record.picking_ids = record.task_id.stock_ids