from odoo import fields, models, api
# TODO: Pendiente validaciones de readonly en campos
# En el historial de aviso no puede existir dos entradas con el mismo folio
# Relacionar a los stock move line los registros de historial


class NoticesHistory(models.Model):

    _name= 'notices.history'


    location_dest = fields.Many2one(
        'stock.location', "Destination Location",
        required=True)

    location_id = fields.Many2one(
        'stock.location', "Source Location",
        required=True)

    quantity = fields.Float(string='Cantidad')



    picking_code = fields.Char(
        string='Tipo de operacion',
    )
    

    notice_id = fields.Many2one('notices.notices', string="Aviso relacionado")



    origin = fields.Char(string='Documento origen')

    folio = fields.Char(string='Folio')
    
    # picking_ids = fields.Many2many(
    #     'stock.picking', 
    #     compute = "_compute_picking_ids",
    #     string='Operaciones de Almacén'
    # )
    
    # @api.depends("origin")
    # def _compute_picking_ids(self):

    #     po = self.env['purchase.order'].search([('name','=',self.origin)])
    #     self.picking_ids = po.picking_ids 

        # Hay que mapear por el producto que se encuentra por picking id





    







