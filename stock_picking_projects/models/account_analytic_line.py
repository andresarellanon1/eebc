from odoo import models, fields, api

class TimesheetLine(models.Model):
    _inherit = 'account.analytic.line'

    pickin_ids = fields.Many2many(
        'stock.picking',
        compute="_compute_pickin_ids",
        string="Operaciones de Inventario"
    )

    @api.depends('task_id.stock_ids')
    def _compute_pickin_ids(self):
        for line in self:
            line.pickin_ids = line.task_id.stock_ids
