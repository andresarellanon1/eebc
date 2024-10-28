from odoo import models, fields, api
import datetime, re
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    bid_code = fields.Char(string='Licitación')
    exchange_rate = fields.Float(string="Tipo de cambio")
    creation_date = fields.Date(string="Creation Date", default=fields.Date.context_today, readonly=True)
    submission_date = fields.Date(string="Submission Date")
    publication_date = fields.Date(string="Publication Date")
    site_supervisor_id = fields.Many2one('res.users', string="Site Supervisor")
    subcontractor_id = fields.Many2one('res.users', string="Subcontractor")
    costo_total_final = fields.Float(string="Costo final", compute="_final_cost", store=True)
    display_costo_total_final = fields.Char(string="Costo Final")
    cambiar = fields.Boolean(string="Cambio", default=False)
    
    product_ids = fields.One2many(
        'product.product', 
        'project_id', 
        string='Products'
    )

    activities_tmpl_id = fields.Many2one(
        'activity.template',  # Referencia al modelo
        string='Plantilla de actividades'
    )

    line_activities_ids = fields.One2many(
        'line.activities',  # Referencia al modelo
        'project_id',
        string='Lineas de actividades'
    )

    taxes_id = fields.Many2many(
        'account.tax',  
        string='Impuestos del cliente',
        help='Select taxes that apply to this project.'
    )

    # Valida la fecha en formato DDMMYY y que no pase de 16 car.
    @api.constrains('bid_code')
    def _check_bid_code_format(self):
        for record in self:
            if record.bid_code:
                if len(record.bid_code) > 16:
                    raise ValidationError("El código no puede tener más de 16 caracteres.")
                
                date_str = record.bid_code[:6]
                try:
                    day = int(date_str[:2])
                    month = int(date_str[2:4])
                    year = int(date_str[4:6]) + 2000 
                    datetime(year, month, day)
                except ValueError:
                    raise ValidationError("La fecha debe ser válida en el formato DDMMYY.")
    
    @api.onchange('activities_tmpl_id')
    def _onchange_activities_tmpl_id(self):
        for record in self:
            record.line_activities_ids = record.activities_tmpl_id.line_activities_ids

    @api.depends('task_id.stock_ids')
    def _compute_pickin_ids(self):
        for record in self:
            record.pickin_ids = record.task_id.stock_ids()

    @api.constrains('currency_id', 'exchange_rate')
    def _check_exchange_rate(self):
        for record in self:
            if record.currency_id and record.currency_id.name == 'USD' and not record.exchange_rate:
                raise ValidationError("El campo 'Tipo de cambio' es obligatorio cuando la moneda es USD.")     

    @api.constrains('currency_id', 'exchange_rate')
    def _check_exchange_rate(self):
        for record in self:
            if record.currency_id and record.currency_id.name == 'USD' and not record.exchange_rate:
                raise ValidationError("El campo 'Tipo de cambio' es obligatorio cuando la moneda es USD.")

    @api.onchange('currency_id', 'exchange_rate', 'taxes_id')
    def _product_currency(self):
        for record in self:
            record.product_ids._onchange_activities_tmpl_id()
            record.product_ids._compute_total_cost()

    @api.onchange('taxes_id', 'currency_id', 'exchange_rate')
    def _final_cost(self):
        for record in self:
            record.costo_total_final = 0 
            for product in record.product_ids:
                total = (product.supplier_cost * product.quantity)
                impuestos = ((total) * record.taxes_id.amount)/100
                origin_currency = product.product_id.product_tmpl_id.last_supplier_last_order_currency_id.name
                
                if product.supplier_cost > 0:
                    costo_total = total + impuestos
                    record.costo_total_final =  record.costo_total_final + costo_total

                    if origin_currency == 'USD' or origin_currency == 'MXN':
                        if origin_currency == 'MXN' and product.cambio == True :
                            record.display_costo_total_final = f"{record.costo_total_final:.2f} USD"
                        elif origin_currency == 'USD' and product.cambio == True :
                            record.display_costo_total_final = f"{record.costo_total_final:.2f} MXN"
                        else:
                            record.display_costo_total_final = f"{record.costo_total_final:.2f} {origin_currency}"

    @api.onchange('cambiar')
    def prueba(self):
        _logger.warning('Entro a la funcion prueba')
        cambiar = False
    

            
            
            
            