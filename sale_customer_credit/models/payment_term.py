from odoo import fields, models


class PaymentTermActive(models.Model):
    _inherit = "account.payment.term"

    payment_term_cash = fields.Boolean(default=False, string="Pago inmediato")
