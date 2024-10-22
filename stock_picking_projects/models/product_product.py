from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    


    quantity = fields.Integer(string='Cantidad')
    reserved_qty = fields.Float(string='Reservado')
    total_cost = fields.Float(string='Costo total', compute="_compute_total_cost", store=True)
    supplier_cost = fields.Float(string='Costo', compute="_compute_total_cost", store=True)
    currency = fields.Char(string="Currency")

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
            tipo_cambio = record.project_id.exchange_rate
            project_currency = record.project_id.currency_id.name

            if record.currency == False:
                record.currency == project_currency

            _logger.warning(f'La divisa del producto es: {record.currency}')
            _logger.warning(f'La divisa del formulario es: {record.project_id.currency_id.name}')

            if project_currency == 'USD' and record.project_id.exchange_rate > 0:
                _logger.warning('Entró al if.')
                if record.currency != 'USD':
                    record.supplier_cost = self.pesos_a_dolares(monto,tipo_cambio)
                    record.currency = 'USD'

                    _logger.warning('Hizo cambio a dolares.')
                    _logger.warning(f'Se cambió la divisa a: {record.currency}')

            elif project_currency == 'MXN' and record.project_id.exchange_rate > 0:
                _logger.warning('Entró al Elif.')
                if record.currency != 'MXN':
                    record.supplier_cost = self.dolares_a_pesos(monto,tipo_cambio)
                    record.currency = 'MXN'

                    _logger.warning('Hizo cambio a pesos.')
                    _logger.warning(f'Se cambió la divisa a: {record.currency}')
            else :
                record.supplier_cost = monto
                _logger.warning('Se activó el método en PRODUCT.PRODUCT')
            
    @api.depends('quantity','product_id','project_id.exchange_rate','project_id.currency_id')
    def _compute_total_cost(self):
        for record in self:
            total = (record.supplier_cost * record.quantity)
            impuestos = ((total) * record.product_id.product_tmpl_id.taxes_id.amount)/100
            tipo_cambio = record.project_id.exchange_rate
            monto = total + impuestos

            record.total_cost = total + impuestos

            if record.currency_id.name == 'USD' and record.project_id.exchange_rate > 0:
                record.total_cost = self.pesos_a_dolares(monto,tipo_cambio)
            elif record.currency_id.name == 'MXN' and record.project_id.exchange_rate > 0:
                record.total_cost = self.dolares_a_pesos(monto,tipo_cambio)
            else : 
                record.total_cost = monto

    def pesos_a_dolares(self, monto, tipo_cambio):
        return monto / tipo_cambio

    def dolares_a_pesos(self, monto, tipo_cambio):
        return monto * tipo_cambio