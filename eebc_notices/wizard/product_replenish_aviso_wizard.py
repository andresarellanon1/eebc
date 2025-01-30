from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProductReplenishAvisoWizard(models.TransientModel):
    _name = 'product.replenish.aviso.wizard'
    _description = "Configuración de Avisos para Reposición"

    replenish_id = fields.Many2one('product.replenish', string="Reposición", required=True)
    aviso_name = fields.Char(string="Nombre del Aviso", required=True)
    folio = fields.Char(string="Folio", required=True)
    aviso_quantity = fields.Float(string="Cantidad", required=True)

    def confirm_aviso_creation(self):
        """Enviar datos a la orden de compra"""
        replenish = self.replenish_id
        purchase_line_vals = {
            'product_id': replenish.product_id.id,
            'product_qty': self.aviso_quantity,
            'name': replenish.product_id.name,
            'aviso_name': self.aviso_name,
            'folio': self.folio,
        }

        # Obtener la orden de compra en proceso o crear una nueva
        purchase_order = self.env['purchase.order'].search([('state', '=', 'draft')], limit=1)
        if not purchase_order:
            purchase_order = self.env['purchase.order'].create({
                'partner_id': replenish.product_id.seller_ids[0].name.id if replenish.product_id.seller_ids else False,
            })

        purchase_order.write({'order_line': [(0, 0, purchase_line_vals)]})
        return {'type': 'ir.actions.act_window_close'}
