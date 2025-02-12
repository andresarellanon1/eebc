from odoo import fields, models, api

class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_time = fields.Float(string="Horas estimadas", compute="_compute_estimated_time", store=True)
    work_shift = fields.Float(string='Jornadas Laborales')

    @api.depends('work_shift')
    def _compute_estimated_time(self):
        """
        Calcula las jornadas de la mano de obra a horas de esta manera se puede utilizar
        la mano de obra de la predeterminada de odoo
        """
        for record in self:
            record.estimated_time = record.work_shift * 8
