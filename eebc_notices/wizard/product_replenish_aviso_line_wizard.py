from odoo import _, api, fields, models

class ProductReplenishAvisoLineWizard(models.TransientModel):
    _name = 'product.replenish.aviso.line.wizard'
    _description = 'Aviso Line for Wizard'

    wizard_id = fields.Many2one('product.replenish.aviso.wizard', string="Wizard")
    name = fields.Char(string="Aviso Name", required=True)
    folio = fields.Char(string="Folio", required=True)
    quantity = fields.Float(string="Quantity", required=True)