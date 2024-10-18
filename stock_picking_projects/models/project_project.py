from odoo import models, fields, api
import datetime, re
from odoo.exceptions import ValidationError

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    bid_code = fields.Char(string='Licitación')
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
                # Validar longitud total
                if len(record.bid_code) > 16:
                    raise ValidationError("El código no puede tener más de 16 caracteres.")
                
                # Validar formato de fecha DDMMYY
                date_str = record.bid_code[:6]
                try:
                    day = int(date_str[:2])
                    month = int(date_str[2:4])
                    year = int(date_str[4:6]) + 2000  # Asumiendo que el año está en el siglo XXI
                    datetime(year, month, day)  # Esto lanzará un ValueError si la fecha es inválida
                except ValueError:
                    raise ValidationError("La fecha debe ser válida en el formato DDMMYY.")
                
                # Validar patrón del resto del string
                pattern = r'^[a-zA-Z0-9]{10}-\d{3}$'  # Ajuste para que acepte cualquier UID de longitud adecuada
                if not re.match(pattern, record.bid_code[6:]):
                    raise ValidationError(
                        "El formato del UID debe ser válido (ejemplo: obrA25-102)."
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

    