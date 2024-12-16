from odoo import models, fields, api



class HistorialQuirurgico(models.Model):
    _name = 'sanatorio.quiroz.historial.quirurgico'
    _description = 'Historial Quirúrgico'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    qx_diagnostico = fields.Char(string="QX Diagnóstico")
    qx_anio = fields.Date(string="QX Año")
    procedimiento = fields.Text(string="Procedimiento")
    qx_comentarios = fields.Text(string="QX Comentarios")

