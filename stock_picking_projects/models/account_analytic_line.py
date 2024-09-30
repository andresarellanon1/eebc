from odoo import models, fields, api

class TimesheetLine(models.Model):
    _inherit = 'account.analytic.line'

    pickin_ids = fields.Many2many(
        'stock.picking',
        string="Operaciones de Inventario"
    )

    
