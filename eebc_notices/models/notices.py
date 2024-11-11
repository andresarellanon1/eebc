from odoo import fields, models, api
# TODO: Pendiente validaciones de readonly en campos

# campo nuevo total computada(sumatoria de la cantidad de historiales)   - lISTO!!

class Notices(models.Model):

    _name= 'notices.notices'    

    # warehouse
    
    product_id = fields.Many2one(
        string='Recurso',
        comodel_name='product.product',
    )
    partner_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
    )
    folio = fields.Char(string='Folio')
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad', compute='_compute_quantity', store=True)
   
    lot_ids = fields.Many2many(
        string='Series',
        comodel_name='stock.lot',
        relation='notices.lot',
        column1='lot_id',
        column2='notices_id',
        compute='_compute_series'
    )
    origin_invoice_ids = fields.Many2many(
        string='Facturas de compra',
        comodel_name='account.move',
        relation='notices.origin.moves',
        column1='account_move_id',
        column2='notice_id',
        compute='_compute_origin_invoice_ids' )

    sale_invoice_ids = fields.Many2many(
        string='Facturas de venta',
        comodel_name='account.move',
        relation='notices.sales.moves',
        column1='account_move_id',
        column2='notice_id',
        compute='_compute_sale_invoice_ids' )

    history_ids = fields.One2many(
        string='Historial de movimientos',
        comodel_name='notices.history',
        inverse_name='notice_id',
    )

    @api.depends('history_ids')
    def _compute_series(self):
        pass


    @api.depends('history_ids')
    def _compute_origin_invoice_ids(self):
        pass

    @api.depends('history_ids')
    def _compute_sale_invoice_ids(self):
        pass

    @api.depends('history_ids.quantity')
    def _compute_quantity(self):
        for record in self:
            # Calcula la suma de las cantidades en history_ids
            record.quantity = sum(record.history_ids.mapped('quantity'))

