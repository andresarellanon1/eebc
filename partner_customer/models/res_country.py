from odoo import models, fields

class ResCountry(models.Model):
    _inherit = 'res.country'

    foreign_name = fields.Char(string="Nacionalidad")