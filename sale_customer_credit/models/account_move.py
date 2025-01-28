import logging
from odoo import api, models
logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Extiende el modelo account.move para agregar funcionalidades personalizadas relacionadas con la gestión de crédito de los partners."""

    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribe el método create para verificar y actualizar el crédito del partner después de crear el asiento.

        Args:
            vals_list (list): Lista de diccionarios con los valores para los nuevos asientos.

        Returns:
            account.move: Los asientos creados.
        """
        moves = super(AccountMove, self).create(vals_list)
        moves._check_and_update_partner_credit()
        return moves

    @api.onchange("partner_id")
    def _onchange_partner_set_addresses_default(self):
        """Método onchange para establecer la dirección de envío como la dirección predeterminada del partner."""
        for move in self:
            move.partner_shipping_id = move.partner_id

    def _check_and_update_partner_credit(self):
        """
        Verifica si se ha alcanzado el límite de crédito del partner y actualiza el estado de suspensión de crédito.

        1. Obtiene el partner relacionado con el movimiento.
        2. Verifica si el límite de crédito ha sido alcanzado mediante el método _check_credit_limit del partner.
        3. Si el límite ha sido alcanzado, se marca el partner con suspensión de crédito (customer_credit_suspend = True).
        """
        for move in self:
            partner = move.partner_id
            limit_reached = partner._check_credit_limit(move.amount_residual)
            if limit_reached:
                partner.customer_credit_suspend = True