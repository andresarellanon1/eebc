from odoo import models, fields, api
import datetime, re
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    bid_code = fields.Char(string='Licitación')
    bid_date = fields.Date()
    exchange_rate = fields.Float(string="Tipo de cambio")
    
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

    @api.constrains('bid_code')
    def _check_bid_code_format(self):
        for record in self:
            if record.bid_code:
                pattern = r'^\d{6}[a-zA-Z]{3}\d{2}-\d{3}$'
                if not re.match(pattern, record.bid_code):
                    raise ValidationError(
                        "El formato de la licitacion debe ser: (171024obrA24-201)."
                    )
    
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

    