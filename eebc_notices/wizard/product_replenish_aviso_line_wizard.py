from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ProductReplenishAvisoLineWizard(models.TransientModel):
    _name = 'product.replenish.aviso.line.wizard'
    _description = 'Aviso Line for Wizard'

    wizard_id = fields.Many2one('product.replenish.aviso.wizard', string="Wizard")
    name = fields.Char(string="Aviso Name", required=True)
    folio = fields.Char(string="Folio", required=True)
    quantity = fields.Float(string="Quantity", required=True,  digits=(12, 0))


    @api.constrains('quantity')
    def _check_quantity_integer(self):
        for line in self:
            if not float(line.quantity).is_integer():
                raise ValidationError(_("The quantity must be an integer (no decimals allowed)."))