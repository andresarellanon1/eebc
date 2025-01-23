
from odoo import models, fields


class Weekday(models.Model):
    _name = 'res.weekday'
    _description = 'Days of the Week'

    name = fields.Char(string='Día', required=True, translate=True)
    number = fields.Integer(string='Núm.', required=True)
