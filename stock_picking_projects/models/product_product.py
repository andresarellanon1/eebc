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
    cambio = fields.Boolean(string="Cambio", default=False)
    display_supplier_cost = fields.Char(string="Costo")
    display_total_cost = fields.Char(string="Total producto")
    
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

                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        record.display_supplier_cost = f"{record.supplier_cost:.2f} {record.currency}"
                    if origin_currency == 'USD':
                        record.cambio = False
                    else:
                        record.cambio = True
                else:
                    if origin_currency == 'USD' or origin_currency == 'MXN': 
                        record.supplier_cost = monto
                        record.display_supplier_cost = f"{record.supplier_cost:.2f} {origin_currency}"

            elif project_currency == 'MXN' and record.project_id.exchange_rate > 0:
                if origin_currency == 'USD' or record.cambio == True :
                    record.supplier_cost = self.dolares_a_pesos(monto,tipo_cambio)
                    record.currency = 'MXN'

                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        record.display_supplier_cost = f"{record.supplier_cost:.2f} {record.currency}"

                    if origin_currency == 'MXN':
                        record.cambio = False
                    else:
                        record.cambio = True
                else:
                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        record.supplier_cost = monto
                        record.display_supplier_cost = f"{record.supplier_cost:.2f} {origin_currency}"
            else :
                if origin_currency == 'USD' or origin_currency == 'MXN':
                    record.supplier_cost = monto
                    record.display_supplier_cost = f"{record.supplier_cost:.2f} {origin_currency}"


    @api.onchange('quantity','product_id')
    def _compute_total_cost(self):
        self._onchange_activities_tmpl_id()
        for record in self:
            total = (record.supplier_cost * record.quantity)
            impuestos = ((total) * record.project_id.taxes_id.amount)/100
            origin_currency = record.product_id.product_tmpl_id.last_supplier_last_order_currency_id.name

            record.total_cost = total + impuestos
        
            if origin_currency == 'USD' or origin_currency == 'MXN':
                if origin_currency == 'MXN' and record.cambio == True :
                    record.display_total_cost = f"{record.total_cost:.2f} USD"
                elif origin_currency == 'USD' and record.cambio == True :
                    record.display_total_cost = f"{record.total_cost:.2f} MXN"
                else:
                    record.display_total_cost = f"{record.total_cost:.2f} {origin_currency}"


    @api.onchange('quantity','product_id')
    def _compute_final_cost(self):
        self.project_id._product_currency()
        self.project_id._final_cost()
        for record in self:
            record.project_id.costo_total_final = 0 
            for project in record.project_id:
                total = (record.supplier_cost * record.quantity)
                impuestos = ((total) * project.taxes_id.amount)/100
                origin_currency = record.product_id.product_tmpl_id.last_supplier_last_order_currency_id.name
                
                if record.supplier_cost > 0:
                    costo_total = total + impuestos
                    project.costo_total_final =  project.costo_total_final + costo_total

                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        if origin_currency == 'MXN' and record.cambio == True :
                            project.display_costo_total_final = f"{project.costo_total_final:.2f} USD"
                        elif origin_currency == 'USD' and record.cambio == True :
                            project.display_costo_total_final = f"{project.costo_total_final:.2f} MXN"
                        else:
                            project.display_costo_total_final = f"{project.costo_total_final:.2f} {origin_currency}"
                            _logger.warning(f'Se le esta dando valor a display costo: {project.display_costo_total_final}')

    @api.onchange('quantity','product_id')
    def funcion_prueba(self):
        for record in self:
            _logger.warning(f'Se activo onchange')
           self.project_id._modificar_campos(record.quantity, 100)


    def pesos_a_dolares(self, monto, tipo_cambio):
        return monto / tipo_cambio

    def dolares_a_pesos(self, monto, tipo_cambio):
        return monto * tipo_cambio