from odoo import api, models


class ProductSelectionWizard(models.TransientModel):
    _name = 'product.selection.wizard'
    _inherit = ['product.selection.wizard']

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # Obtener productos bajo un contexto específico
        products = self.env['product.product'].search([('type', '=', 'product')])
        lines = [(0, 0, {'product_id': product.id, 'quantity': 1.0}) for product in products]
        res['quantity_ids'] = lines
        return res

class ProductSelectionWizard(models.TransientModel):
    _inherit = 'product.selection.wizard'

    def action_confirm(self):
        for line in self.quantity_ids:
            # Realiza la lógica que necesites con los productos y cantidades
            self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                # Agregar otros campos según sea necesario
            })
        return {'type': 'ir.actions.act_window_close'}