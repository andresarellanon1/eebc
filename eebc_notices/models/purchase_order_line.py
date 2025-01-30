class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    aviso_name = fields.Char(string="Nombre del Aviso")
    folio = fields.Char(string="Folio")
    aviso_quantity = fields.Float(string="Cantidad del Aviso")