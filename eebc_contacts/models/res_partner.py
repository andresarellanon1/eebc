from odoo import fields, models, api

class ResPartner(models.Model):

    _inherit = 'res.partner'

    is_customer = fields.Boolean(default= False, string="Es cliente")
    is_supplier = fields.Boolean(default= False, string="Es proveedor")

    supplier_taxes = fields.Selection(
        string="Impuestos",
        selection=[('resico','Resico'), 
                   ('isr_hon','ISR Honorarios'), 
                   ('isr_ar','ISR Arrendamiento'),
                   ('ret_iva','Retención de IVA Arrendamiento')
                   ]
    )

    @api.onchange('is_supplier')
    def _onchange_is_supplier(self):
        if not self.is_supplier:
            self.supplier_taxes = None