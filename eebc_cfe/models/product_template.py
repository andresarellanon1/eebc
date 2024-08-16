from odoo import fields, models, api

class ProductTemplate(models.Model):

    _inherit= 'product.template'

    is_doc_cfe = fields.Boolean(default= False, string = 'Documento de CFE')
    
