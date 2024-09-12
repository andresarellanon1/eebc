from odoo import fields, models, api

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    complete_description = fields.Char(string="Descripción", compute='_compute_complete_description', store=True)
    use_large_description = fields.Boolean(string="Usar descripción larga", default=False)


    @api.depends('sale_line_ids')
    def _compute_complete_description(self):
        for line in self:
            sale_line = line.sale_line_ids[:1]  # Obtener la primera línea de venta relacionada
            line.complete_description = sale_line.complete_description if sale_line else ''