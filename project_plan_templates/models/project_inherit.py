from odoo import models, fields

class ProjectInherit(models.Model):
    _inherit = 'project.project'

    project_picking_lines = fields.One2many(
        'stock.move',  # Cambia por el modelo correcto si no es stock.move
        'project_id',
        string="Líneas de Inventario"
    )
