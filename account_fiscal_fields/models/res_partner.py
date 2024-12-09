from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging

logger = logging.getLogger(__name__)

EDI_USAGE = [
    ('CP01', 'Pagos'),
]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_usage = fields.Selection(selection_add=EDI_USAGE)