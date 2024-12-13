from odoo import fields, models, api

class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    estimated_time = fields.Float(string="Horas estimadas")