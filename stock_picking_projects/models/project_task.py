from odoo import models, fields, api

class ProjectTask(models.Model):

    _inherit = 'project.task'

    stock_ids = fields.One2many('stock.picking', 'project_id', string="stock")
    move_ids = fields.One2many('stock.move', 'task_id', string="Lineas de operaciones")

    