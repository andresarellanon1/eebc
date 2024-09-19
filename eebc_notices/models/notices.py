from odoo import fields, models, api

class Notices(models.Model):

    _name= 'notices.notices'    
    
    resource = fields.Many2one(
        string='Recurso',
        comodel_name='product.product',
    )
    
 
    supplier = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
    )
    
    folio = fields.Char(string='Folio')
    create_date = fields.Date(
        string='Fecha de creacion',
        default=fields.Date.context_today,
    )
    
  
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad')
    series = fields.Char(string='Series (s)')

    picking_ids = fields.Many2many(
        'stock.picking', 
        string='Operaciones de Almacén'
    )
    
    
