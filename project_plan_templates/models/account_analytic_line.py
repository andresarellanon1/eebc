from odoo import fields, models, api

class AccountAnalytics(models.Model):
    _inherit = 'account.analytic.line'

    project_plan_line = Many2one('project.plan.line', string="Project plan line")