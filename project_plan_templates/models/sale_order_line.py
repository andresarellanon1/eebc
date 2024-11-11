from odoo import fields, models, api

class SaleOrderLinea(models.Model):

    _inherit = 'sale.order.line'

    use_for_project = fields.Boolean(default=False)