from odoo import fields, api, models 

class TaskInventoryLine(models.TransientModel):
    _name = 'task.inventory.line'
    _description = 'Line to assign products to task inventory'

    task_id = fields.Many2one('project.task', string="Tarea")

    product_id = fields.Many2one('product.product', string="Producto")
    quantity = fields.Float(string='Cantidad')
    product_uom_id = fields.Many2one('uom.uom', string='Unidad de medida')
    product_packaging_id = fields.Many2one('product.packaging', string='Embalaje')
    product_uom_qty = fields.Float(string="Demanda")