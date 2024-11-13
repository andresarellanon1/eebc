from odoo import fields, models, api

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    task_inventory_lines = fields.One2many('task.inventory.line', 'stock_picking')

    task_id = fields.Many2one('project.task', string='projects')
    project_id = fields.Many2one('project.project', string='Proyecto')
    new_selection = fields.Selection(string='Nueva selección', copy=False,selection=[('estimacion','Estimación'),('traslado','Traslado')])
    transport_type = fields.Selection( string="Tipo de transporte",selection=[('00', 'No usa carreteras federales'), ('01', 'Autotransporte Federal')])
    
    custom_document_identification = fields.Char(string="Customs Document Identification")
    lat_origin = fields.Float(string="Latitud de origen")
    long_origin = fields.Float(string="Longitud de origen")
    lat_dest = fields.Float(string="Latitud de destino")
    long_dest = fields.Float(string="Longitud de destino")