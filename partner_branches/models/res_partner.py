
import logging
from odoo import models, fields, api, exceptions

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_branch = fields.Boolean(default=False, string="Es sucursal")
    branch_id = fields.Many2one(
        'res.partner', string="Sucursal",
        domain="[('is_branch', '=', True), ('parent_id', '=', parent_id)]"
    )
    branch_name = fields.Char(string="Nombre de sucursal")
    branch_number = fields.Char(string="Número de sucursal")

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        partners._apply_branch_rules()
        return partners

    def _apply_branch_rules(self):
        for partner in self:

            if partner.type == 'contact':
                partner.is_branch = False
                partner.branch_name = False
                partner.branch_number = False
                partner.branch_tax = False

            if not partner.parent_id and partner.branch_id:
                partner.branch_id = False

            if partner.parent_id:

                if partner.parent_id.customer_number_reference:
                    partner.customer_number_reference = partner.parent_id.customer_number_reference

                if partner.parent_id.commercial_name:
                    partner.commercial_name = partner.parent_id.commercial_name

                if partner.is_branch:
                    partner.name = partner.branch_name

    @api.constrains('type', 'parent_id', 'is_branch')
    def _check_branch_constraints(self):
        for partner in self:
            if partner.type == 'contact' and partner.is_branch:
                raise exceptions.ValidationError("Contact records cannot be branches.")
            if partner.is_branch and not partner.parent_id:
                raise exceptions.ValidationError("Branch partners must have a parent partner.")

    @api.onchange('type')
    def _onchange_type(self):
        for partner in self:
            if partner.type == 'contact':
                partner.is_branch = False

    @api.onchange('branch_name', 'is_branch', 'parent_id')
    def _onchange_branch_info(self):
        for partner in self:
            if partner.is_branch and partner.parent_id:
                partner.name = partner.branch_name
            elif not partner.is_branch:
                partner.branch_name = False
                partner.branch_number = False
                partner.branch_tax = False
