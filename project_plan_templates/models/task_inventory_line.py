from odoo import fields, api, models 

class TaskInventoryLine(models.TransientModel):
    _name = 'task.inventory.line'
    _description = 'Line to assign products to task inventory'

    inventory_id = fields.Many2one('task.inventory.wizard')
    task_id = fields.Many2one('project.task', string="Tarea")
    stock_picking = fields.Many2one('stock.picking')

    product_id = fields.Many2one('product.product', string="Producto")
    quantity = fields.Float(string='Cantidad')
    product_uom = fields.Many2one('uom.uom', string='Unidad de medida')
    product_packaging_id = fields.Many2one('product.packaging', string='Embalaje')
    product_uom_qty = fields.Float(string="Demanda")
    name = fields.Char(string='Descripción')
    max_quantity = fields.Float(string='Cantidad máxima')

    @api.onchange('task_id')
    def _onchange_task_id(self):
        for record in self:
            if record.product_id: 
                record.name = (record.name or '') + record.product_id.display_name
                record.name = record.name + " X "
                record.name = record.name + record.product_uom_qty
