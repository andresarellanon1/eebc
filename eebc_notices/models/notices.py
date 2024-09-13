from odoo import fields, models, api

class Notices(models.Model):

    _name= 'notices.notices'

    resource = fields.Float()
 
    supplier = fields.Char( string='Proveedor')
    folio = fields.Char(string='Folio')
    create_date = fields.Date(
        string='Fecha de creacion',
        default=fields.Date.context_today,
    )
    
  
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad')
    series = fields.Char(string='Series (s)')

     # Relación One2many con órdenes de compra
    order_ids = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='notice_id',
        string='Órdenes de compra'
    )
    
    # Relación Many2many con facturas (a través de las órdenes de compra)
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string='Facturas',
        compute='_compute_invoices'
    )

    @api.depends('order_ids')
    def _compute_invoices(self):
        for record in self:
            invoices = self.env['account.move'].search([('invoice_origin', 'in', record.order_ids.mapped('name'))])
            record.invoice_ids = invoices


 