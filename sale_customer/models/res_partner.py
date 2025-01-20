from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    HOURS = [
        ('00:00', '00:00'),
        ('01:00', '01:00'),
        ('02:00', '02:00'),
        ('03:00', '03:00'),
        ('04:00', '04:00'),
        ('05:00', '05:00'),
        ('06:00', '06:00'),
        ('07:00', '07:00'),
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
        ('20:00', '20:00'),
        ('21:00', '21:00'),
        ('22:00', '22:00'),
        ('23:00', '23:00')
    ]

    is_customer = fields.Boolean(default=False, string="Es cliente")
    commercial_name = fields.Char(string="Nombre comercial")
    customer_need_purchase_order = fields.Boolean(
        default=False,
        string="Requiere orden de compra.",
        help="Activar este campo habilita la validación de la referencia de orden de compra del cliente en los documentos de venta.")
    customer_bday = fields.Date(string="Cumpleaños del cliente.")
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
