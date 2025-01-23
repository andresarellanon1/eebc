from odoo import fields, models, api

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    task_id = fields.Many2one('project.task', string='projects')
    project_id = fields.Many2one('project.project', string='Proyecto')
    new_selection = fields.Selection(string='Nueva selección', copy=False,selection=[('estimacion','Estimación'),('traslado','Traslado')])