from odoo import fields, models, api
class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    aviso_name = fields.Char(string="Nombre del Aviso")
    aviso_folio = fields.Char(string="Folio")
    aviso_quantity = fields.Float(string="Cantidad del Aviso")