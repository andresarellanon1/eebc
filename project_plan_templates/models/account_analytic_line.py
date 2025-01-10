from odoo import fields, models, api

class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_time = fields.Float(string="Horas estimadas")
    work_shift = fields.Float(string='Jornadas Laborales')

    @api.onchange('work_shift')
    def _work_shift_onchange_(self):
        for record in self:
            record.estimated_time = record.work_shift * 8
