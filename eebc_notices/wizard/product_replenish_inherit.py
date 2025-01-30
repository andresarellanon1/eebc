from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProductReplenishInherit(models.TransientModel):
    _inherit = 'product.replenish'

    has_aviso = fields.Boolean(compute="_compute_has_aviso", string="Con Aviso")
    aviso_lines = fields.One2many('product.replenish.aviso.line', 'replenish_id', string="Aviso Lines")

    @api.depends('product_id')
    def _compute_has_aviso(self):
        for rec in self:
            rec.has_aviso = rec.product_id.is_aviso

    def action_open_aviso_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Aviso Details'),
            'res_model': 'product.replenish.aviso.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_replenish_id': self.id,
                'default_total_qty': self.quantity,
            },
        }

    def _prepare_run_values(self):
        res = super(ProductReplenishInherit, self)._prepare_run_values()
        if self.has_aviso and self.aviso_lines:
            # Agregar información de avisos a las líneas de la orden de compra
            res['order_line'] = [(0, 0, {
                'product_id': self.product_id.id,
                'product_qty': line.quantity,
                'aviso_name': line.name,
                'aviso_folio': line.folio,
                'aviso_quantity': line.quantity,
            }) for line in self.aviso_lines]
        return res