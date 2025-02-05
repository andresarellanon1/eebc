from odoo import fields, models


class PaymentTermActive(models.Model):
    """Extiende el modelo account.payment.term para agregar un campo que indica si el término de pago es inmediato."""

    _inherit = "account.payment.term"

    payment_term_cash = fields.Boolean(default=False, string="Pago inmediato")