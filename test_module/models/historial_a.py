from odoo import models, fields, api



class HistorialAlergias(models.Model):
    _name = 'sanatorio.quiroz.historial.alergias'
    _description = 'Historial Alergias'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    alergeno = fields.Selection([
        ('polen', 'Polen'), ('polvo', 'Polvo'), ('otros', 'Otros')
    ], string="Alergeno")
    rxa_anio = fields.Date(string="RXA Año")
    reaccion = fields.Text(string="Reacción")
    tratamiento = fields.Text(string="RXA Tratamiento")

