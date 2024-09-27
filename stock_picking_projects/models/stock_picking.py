from odoo import fields, models, api

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.task', string='projects')