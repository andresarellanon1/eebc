from odoo import fields, models, api

class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_time = fields.Float(string="Horas estimadas", compute="_compute_estimated_time", store=True)
    work_shift = fields.Float(string='Jornadas Laborales')

    @api.depends('work_shift')
    def _compute_estimated_time(self):
        for record in self:
            record.estimated_time = record.work_shift * 8
