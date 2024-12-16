from odoo import models, fields, api




class Tratamiento(models.Model):
    _name = 'sanatorio.quiroz.tratamiento'
    _description = 'Tratamiento'

    historial_clinico_id = fields.Many2one('sanatorio.quiroz.historial.clinico', string="Historial Clínico")
    medicamento = fields.Char(string="Medicamento")
    presentacion = fields.Text(string="Presentación")
    dosis = fields.Integer(string="Dosis")
    frecuencia = fields.Float(string="Frecuencia")
    duracion = fields.Integer(string="Duración")

