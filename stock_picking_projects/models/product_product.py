from odoo import models, fields, api
import logging

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    quantity = fields.Integer(string='Cantidad')
    reserved_qty = fields.Float(string='Reservado')
    total_cost = fields.Float(string='Costo total', compute="_compute_total_cost", store=True)
    supplier_cost = fields.Float(string='Costo', compute="_compute_total_cost", store=True)
    currency = fields.Char(string="Currency")
    cambio = fields.Boolean(string="Cambio", default=False)
    display_supplier_cost = fields.Char(string="Costo con moneda")

    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto',
        store = True,
        copied = True
    )

    product_id = fields.Many2one(
        'product.product', 
        string='Producto',
        store = True,
        copied = True
    )

    @api.onchange('product_id','currency')
    def _onchange_activities_tmpl_id(self):
        for record in self:
            record.name = record.product_id.name
            monto = record.product_id.product_tmpl_id.last_supplier_last_price
            origin_currency = record.product_id.product_tmpl_id.last_supplier_last_order_currency_id.name
            tipo_cambio = record.project_id.exchange_rate
            project_currency = record.project_id.currency_id.name

            if record.currency == False:
                record.currency == project_currency

            if project_currency == 'USD' and record.project_id.exchange_rate > 0:
                if origin_currency == 'MXN' or record.cambio == True :
                    record.supplier_cost = self.pesos_a_dolares(monto,tipo_cambio)
                    record.currency = 'USD'

                    if origin_currency == 'USD':
                        record.cambio = False
                    else:
                        record.cambio = True
                else:
                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        record.supplier_cost = monto
                        display_supplier_cost = str(record.supplier_cost) + ' ' + origin_currency

            elif project_currency == 'MXN' and record.project_id.exchange_rate > 0:
                if origin_currency == 'USD' or record.cambio == True :
                    record.supplier_cost = self.dolares_a_pesos(monto,tipo_cambio)
                    record.currency = 'MXN'

                    if origin_currency == 'MXN':
                        record.cambio = False
                    else:
                        record.cambio = True
                else:
                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        record.supplier_cost = monto
                        display_supplier_cost = str(record.supplier_cost) + ' ' + origin_currency
            else :
                if origin_currency == 'USD' or origin_currency == 'MXN':
                    record.supplier_cost = monto
                    display_supplier_cost = str(record.supplier_cost) + ' ' + origin_currency

            
    @api.depends('quantity','product_id','project_id.exchange_rate','project_id.currency_id')
    def _compute_total_cost(self):
        for record in self:
            total = (record.supplier_cost * record.quantity)
            impuestos = ((total) * record.product_id.product_tmpl_id.taxes_id.amount)/100

            record.total_cost = total + impuestos

    def pesos_a_dolares(self, monto, tipo_cambio):
        return monto / tipo_cambio

    def dolares_a_pesos(self, monto, tipo_cambio):
        return monto * tipo_cambio