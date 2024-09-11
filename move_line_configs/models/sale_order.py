from odoo import fields, models, api

class SaleOrder(models.Model):

    _inherit = "sale.order"

    use_large_description = fields.Boolean(string="Usar descripción larga", default=False)