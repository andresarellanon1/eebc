from odoo import models, fields, api

class TimesheetLine(models.Model):
    _inherit = 'account.analytic.line'

    pickin_ids = fields.Many2many(
        'stock.picking',
        string="Operaciones de Inventario"
    )

    """domain_pickin_ids = fields.Many2many(
        'stock.picking',
        compute="_compute_pickin_ids"
    )

    @api.depends('task_id.stock_ids')
    def _compute_pickin_ids(self):
        for line in self:
            pickins = line.task_id.stock_ids
            ids = pickins.mapped('id')
            
            line.pickin_ids = self.env['stock.picking'].search([('task_id','in', ids)])"""

    
