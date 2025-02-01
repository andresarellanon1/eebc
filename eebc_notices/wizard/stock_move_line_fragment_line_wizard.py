from odoo import models, fields, api

class StockMoveLineFragmentLine(models.TransientModel):
    _name = 'stock.move.line.fragment.line'
    _description = 'Líneas de Fragmentación'

    wizard_id = fields.Many2one('stock.move.line.fragment.wizard', string="Wizard de Fragmentación", required=True)
    quantity = fields.Float(string="Cantidad", required=True)