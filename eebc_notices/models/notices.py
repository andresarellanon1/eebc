from odoo import fields, models, api

class Notices(models.Model):

    _name= 'notices.notices'

    resource = fields.Float()
    order = fields.Many2one(
        string='Orden de compra origen',
        comodel_name='purchase.order',
        ondelete='restrict',
    )
    supplier = fields.Char( string='Proveedor')
    folio = fields.Char(string='Folio')
    create_date = fields.Date(
        string='Fecha de creacion',
        default=fields.Date.context_today,
    )
    
    invoices = fields.Many2one(
        string='Facturas',
        comodel_name='account.move',
    )
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad')
    series = fields.Char(string='Series (s)')
