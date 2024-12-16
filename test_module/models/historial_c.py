from odoo import models, fields, api



class HistorialClinico(models.Model):
    _name = 'sanatorio.quiroz.historial.clinico'
    _description = 'Historial Clínico'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    intervencion = fields.Selection([('consulta', 'Consulta'), ('ingreso', 'Ingreso')], string="Intervención")
    diagnostico = fields.Char(string="Diagnóstico")
    dx_anio = fields.Date(string="DX Año")
    tratamiento_id = fields.Many2one('sanatorio.quiroz.tratamiento', string="Tratamiento")
    dx_evolucion = fields.Text(string="DX Evolución")
    dx_comentarios = fields.Text(string="DX Comentarios")
