from odoo import fields, models, api

class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_time = fields.Float(string="Horas estimadas")
    work_shift = fields.Float(string='Jornadas Laborales')

    def _compute_work_hours(self):
        for record in self:
            record.estimated_time = record.work_shift * 8
