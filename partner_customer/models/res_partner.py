from odoo import models, fields, api
import logging
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

    @api.constrains('vat', 'country_id')
    def check_vat(self):
        """
            TL;DR:
                The current Odoo base VAT validation marks several legitimate RFCs (Mexican VAT) as "invalid,"
                even though they're fully compliant with the Mexican tax authority (SAT).
                So... we nuked the validation. <3

            Why?:
                - I couldn't find a way to add a flag to bypass VAT validation.
                Sure, it *might* be feasible to handle via context, but realistically, I can't guarantee consistent context values
                across multiple workflows that create partners.
                - There's no valid reason to expect invalid VATs.
                - If there's an invalid VAT, so be it. The PAC will return a verbose error, nothing bad can happen for having a wrong vat stored.
                - As far as I know, Odoo isn't an official tool distributed by the Mexican government:
                It has no authority to decide if an RFC (VAT) is valid—especially not with a REGEX!?
                - This bug might actually be a "skill issue" from whoever wrote that regex... which only reinforces why
                it's reckless to use regex for cases like this.

            Note: I said "reckless" not "wrong" because while it's not outright wrong to use regex in important piece of software,
                hilariously it always happens to fail at some point.

            Anyway, I don’t care. I removed the entire method. Enjoy. :)
            - j
        """
        return
