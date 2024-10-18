from odoo import models, fields, api
import datetime

class ProjectProject(models.Model):

    _inherit = 'project.project'

    default_picking_type_id = fields.Many2one('stock.picking.type', string="Operation type", required=True)
    pickin_ids = fields.Many2many('stock.picking', string="Operaciones de Inventario")
    bid_date = fields.Date(string="Fecha de licitación")
    bid_string = fields.String(string="Clave de licitacion", readonly=True)
    
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

    