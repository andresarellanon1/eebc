from odoo import fields, models


class PaymentTermActive(models.Model):
    _inherit = "account.payment.term"

    """
    Extiende el modelo 'account.payment.term' para añadir un campo que indica 
    si el término de pago es "Pago inmediato".
    """

    payment_term_cash = fields.Boolean(default=False, string="Pago inmediato")
