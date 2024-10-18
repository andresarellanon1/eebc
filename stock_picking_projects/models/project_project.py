from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
from datetime import datetime

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    bid_date = fields.Date(string="Fecha de licitación")
    bid_string = fields.Char(string="Clave de licitación", readonly=True)
    exchange_rate = fields.Float(string="Tipo de cambio")
    creation_date = fields.Date(string="Creation Date", default=fields.Date.context_today, readonly=True)
    submission_date = fields.Date(string="Submission Date")
    publication_date = fields.Date(string="Publication Date")
    
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

    @api.onchange('bid_date')
    def bid_date_onchange_(self):
        for record in self:
            code = record.id
            date = datetime.strptime(record.bid_date, "%Y-%m-%d")
            day = f"{date.day:02}"
            month = f"{date.month:02}"
            year = f"{date.year % 100:02}"

            record.bid_string = "{day}{month}{year}{code}"

    
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

    