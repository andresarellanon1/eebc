from odoo import models, fields, api

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    product_ids = fields.Many2many('product.product', string='Products')

    actividad_ids = fields.One2many(
        'activity.template',  # Referencia al modelo
        'project_id',     # Campo Many2one
        string='Actividades'
    )

    # actividad_id = fields.Many2one(
    #     'project.project',  # Referencia al mismo modelo
    #     string='Actividad',
    #     store = True,
    #     copied = True
    # )
    

    @api.depends('task_id.stock_ids')
    def _compute_pickin_ids(self):
        for record in self:
            record.pickin_ids = record.task_id.stock_ids