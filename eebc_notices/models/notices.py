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
    

    
    notice = fields.Char(string='Aviso')
    description = fields.Char(string='Descripción')
    quantity = fields.Float(string='Cantidad', compute='_compute_quantity', store=True)
    
    # stock_location_origin_id = fields.Many2one(
    #     string='Almacen origen',
    #     comodel_name='stock.location',        
    #     compute='_compute_location_origin_id'
    # )
    name = fields.Char(
            string='Name',
            compute='_compute_name',
            store=True,
            readonly=True
        )

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
        compute='_compute_origin_invoice_ids' 
    )
    sale_invoice_ids = fields.Many2many(
        string='Facturas de venta',
        comodel_name='account.move',
        relation='notices.sales.moves',
        column1='account_move_id',
        column2='notice_id',
        compute='_compute_sale_invoice_ids' 
    )
    history_ids = fields.One2many(
        string='Historial de movimientos',
        comodel_name='notices.history',
        inverse_name='notice_id',
    )

    # @api.depends('history_ids')
    # def _compute_location_origin_id(self):
    #     for notice in self:
    #         for history_record in notice.history_ids:
    #             if history_record.location_dest:
    #                 self.stock_location_origin_id.append(history_record.location_dest) 
                    
    
    
    @api.depends('notice')
    def _compute_name(self):
        for record in self:
            # Concatenar 'Aviso' al valor del campo `notice`
            record.name = f"Aviso {record.notice}" if record.notice else "Aviso sin nombre"

    @api.depends('history_ids')
    def _compute_series(self):
        for notice in self:
            lot_set = set()
            for history_record in notice.history_ids:
                stock_move = history_record.stock_move_id
                if stock_move:
                    for lot in stock_move.lot_ids:
                        lot_set.add(lot.id)
            notice.lot_ids = [(6, 0, list(lot_set))]

    @api.depends('history_ids')
    def _compute_origin_invoice_ids(self):
        for notice in self:
            invoice_set = set()
            for history_record in notice.history_ids:
                purchase_order = history_record.purchase_order_id
                if purchase_order:
                    for invoice in purchase_order.invoice_ids:
                        invoice_set.add(invoice.id)
            notice.origin_invoice_ids = [(6, 0, list(invoice_set))]

    @api.depends('history_ids')
    def _compute_sale_invoice_ids(self):
        for notice in self:
            invoice_set = set()
            for history_record in notice.history_ids:
                sale_order = history_record.sale_order_id
                if sale_order:
                    for invoice in sale_order.invoice_ids:
                        invoice_set.add(invoice.id)
            notice.sale_invoice_ids = [(6, 0, list(invoice_set))]

    @api.depends('history_ids.quantity')
    def _compute_quantity(self):
        for record in self:
            approved_history = record.history_ids.filtered(lambda h: h.state == 'approved')
            record.quantity = sum(approved_history.mapped('quantity'))



# cuando es outgoing el picking que seleccione el aviso de donde sacaremos los productos, si es que los productos ya tienen un aviso relacionado con su serie

# mostrar en la vista de stock.picking que se accede desde la orden de venta para que aparezca el boton de crear o seleccionar aviso
# cantidadesdes demandadas y cantidades que hay en el aviso validarlo al momento de darle salida a los productos vendidos en la venta y que el 
#  historialo tenga un estado de draft y done donde hasya que no este validada no se umestre en el historial de avisos