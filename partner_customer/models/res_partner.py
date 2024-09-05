from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import re
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer = fields.Boolean(default=False, string="Es cliente")
    is_government = fields.Boolean(default=False, string="Es del gobierno")


    commercial_name = fields.Char(string="Nombre comercial")

    customer_number_reference = fields.Char(string="Referencia del cliente.")

    @api.onchange('parent_id')
    def _compute_commercial_name_parent_commercial_name(self):
        for partner in self:
            if partner.parent_id:
                partner.commercial_name = partner.parent_id.commercial_name

    @api.onchange('parent_id', 'customer_number_reference', 'parent_id.customer_number_reference')
    def _compute_parent_customer_number_reference(self):
        for partner in self:
            if partner.parent_id:
                partner.customer_number_reference = partner.parent_id.customer_number_reference
            elif (not partner.parent_id):
                # aquí se debería establecer la referencia de cliente actualizada para los hijos
                # TODO: Averiguar si queremos o no queremos hacer eso... creo que si
                continue

    # Remove VAT validation.
    # I couldn't find a way to add the flag to avoid VAT validation,
    # and there is no reason to expect invalid vats.
    # Anyways if theres an invalid vat it will just be or there was an user error of some sort
    # The current odoo base vat validation checks as "invalid" several actual RFC (Vat MX) that are OK and up to date with the MX SAT

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        return
