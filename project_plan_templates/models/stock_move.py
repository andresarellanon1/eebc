from odoo import fields, models, api

class StockMove(models.Model):
   
    _inherit = 'stock.move'

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        domain=lambda self: self._get_product_domain()
    )

    @api.model
    def _get_product_domain(self):
        # Aquí puedes obtener el contexto necesario para determinar el dominio.
        if self.picking_id and self.picking_id.task_id and self.picking_id.task_id.project_id:
            # Obtener los IDs de los productos de project_picking_lines
            product_id = self.picking_id.task_id.project_id.project_picking_lines.mapped('product_id')
            return [('id', 'in', product_id)]
        return []

    # stock.move (picking_id) - stock.picking (task_id) - project.task (project_id) - project.project (project_picking_lines) project.project (project_picking_ids)