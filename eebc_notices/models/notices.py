from odoo import fields, models, api
# TODO: Pendiente validaciones de readonly

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

    last_update = fields.Date(
        string='Ultima actualizacion',
        
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

    
    history_ids = fields.One2many(
        string='Historial de movimientos',
        comodel_name='notice.history',
        inverse_name='notice_id',
    )
    

