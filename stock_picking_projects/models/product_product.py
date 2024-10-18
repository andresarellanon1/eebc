from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    quantity = fields.Integer(string='Cantidad')
    reserved_qty = fields.Float(string='Reservado')
    total_cost = fields.Float(string='Costo total', compute="_compute_total_cost", store=True)
    supplier_cost = fields.Float(string='Costo', compute="_compute_total_cost", store=True)
    
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

    @api.onchange('product_id')
    def _onchange_activities_tmpl_id(self):
        for record in self:
            record.name = record.product_id.name
            monto = record.product_id.product_tmpl_id.last_supplier_last_price
            tipo_cambio = record.project_id.exchange_rate

            if record.currency_id.name == 'USD' and record.project_id.exchange_rate > 0:
                record.supplier_cost = pesos_a_dolares(monto,tipo_cambio)

            if record.currency_id.name == 'MXN' and record.project_id.exchange_rate > 0:
                record.supplier_cost = dolares_a_pesos(monto,tipo_cambio)
            
    @api.depends('quantity','product_id','project_id.exchange_rate','project_id.currency_id')
    def _compute_total_cost(self):
        for record in self:
            total = (record.supplier_cost * record.quantity)
            impuestos = ((total) * record.product_id.product_tmpl_id.taxes_id.amount)/100
            tipo_cambio = record.project_id.exchange_rate
            monto = total + impuestos

            if record.currency_id.name == 'USD' and record.project_id.exchange_rate > 0:
                record.total_cost = pesos_a_dolares(monto,tipo_cambio)

            if record.currency_id.name == 'MXN' and record.project_id.exchange_rate > 0:
                record.total_cost = dolares_a_pesos(monto,tipo_cambio)


    def pesos_a_dolares(self, monto, tipo_cambio):
        return monto / tipo_cambio

    def dolares_a_pesos(self, monto, tipo_cambio):
        return monto * tipo_cambio