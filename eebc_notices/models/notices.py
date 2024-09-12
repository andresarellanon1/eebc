from odoo import fields, models, api

class Notices(models.Model):

    _name= 'notices.notices'

    resource = fields.Float()
    order = fields.One2many(
        string='Orden de compra origen',
        comodel_name='purchase.order',
        inverse_name='purchase_order_notice_id',
    )
    
    supplier = fields.Char( string='Proveedor')
    folio = fields.Char(string='Folio')
    create_date = fields.Date(
        string='Fecha de creacion',
        default=fields.Date.context_today,
    )
    
    invoices = fields.One2many(
        string='Facturas',
        comodel_name='account.move',
        inverse_name='account_move_notice_id',
    )
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad')
    series = fields.Char(string='Series (s)')
