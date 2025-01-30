from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class ProductReplenishAvisoWizard(models.TransientModel):
    _name = 'product.replenish.aviso.wizard'

    _description = 'Wizard for Aviso Details'

    replenish_id = fields.Many2one('product.replenish', string="Replenish", required=True)
    total_qty = fields.Float(string="Total Quantity", readonly=True)
    aviso_lines = fields.One2many('product.replenish.aviso.line.wizard', 'wizard_id', string="Aviso Lines")

    def action_confirm(self):
        self.ensure_one()
        if sum(line.quantity for line in self.aviso_lines) > self.total_qty:
            raise ValidationError(_("The total quantity of avisos cannot exceed the total quantity specified."))
        self.replenish_id.aviso_lines = [(0, 0, {
            'name': line.name,
            'folio': line.folio,
            'quantity': line.quantity,
        }) for line in self.aviso_lines]
        return self.replenish_id.launch_replenishment() 