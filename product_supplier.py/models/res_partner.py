from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_supplier = fields.Boolean(default= False, string = "Es proveedor")
    supplier_number_reference = fields.Char(string="Referencia de proveedor")