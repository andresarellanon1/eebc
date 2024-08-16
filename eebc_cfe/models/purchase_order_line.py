from odoo import fields, models, api

class PurchaseOrders(models.Model):

    _inherit = "purchase.order.line"