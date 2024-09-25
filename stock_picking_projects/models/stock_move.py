from odoo import fields, models, api

class StockMove(models.Model):

    _inherit = 'stock.move'

    task_id = fields.Many2one('project.task')