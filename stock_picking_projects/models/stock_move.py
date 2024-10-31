from odoo import _, fields, models, api

class StockMove(models.Model):
    _inherit = "stock.move"

    task_id = fields.Many2one('project.task', string="Task", help="Task associated with this stock move.")
