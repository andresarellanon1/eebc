from odoo import _, api, fields, models

class ProductReplenishAvisoLine(models.TransientModel):
    _name = 'product.replenish.aviso.line'
    _description = 'Aviso Line for Product Replenish'

    replenish_id = fields.Many2one('product.replenish', string="Replenish")
    name = fields.Char(string="Aviso Name", required=True)
    folio = fields.Char(string="Folio", required=True)
    quantity = fields.Float(string="Quantity", required=True)
