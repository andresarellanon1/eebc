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
        for line in self.aviso_lines:
            if not float(line.quantity).is_integer():
                raise ValidationError(_("The quantity for Aviso '%s' must be an integer (no decimals allowed).") % line.name)
        if sum(line.quantity for line in self.aviso_lines) > self.total_qty:
            raise ValidationError(_("The total quantity of avisos cannot exceed the total quantity specified."))

        # Crear una nueva orden de compra
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.replenish_id.supplier_id.partner_id.id,
            'date_order': fields.Datetime.now(),
            'company_id': self.replenish_id.company_id.id,
        })

        # Crear las líneas de la orden de compra basadas en las líneas de aviso
        for line in self.aviso_lines:
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': self.replenish_id.product_id.id,
                'product_qty': line.quantity,
                'name': f"Aviso: {line.name} - Folio: {line.folio}",  # Incluir nombre y folio del aviso
                'aviso_name': line.name,  # Almacenar el nombre del aviso
                'aviso_folio': line.folio,  # Almacenar el folio del aviso
                "aviso_quantity": line.quantity,
                'price_unit': self.replenish_id.product_id.standard_price,  # Precio estándar del producto
                'date_planned': self.replenish_id.date_planned,
            })

        # Confirmar la orden de compra
        purchase_order.button_confirm()

        # Retornar una acción para abrir la orden de compra creada
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }