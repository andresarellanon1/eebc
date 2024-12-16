from odoo import models, fields, api



class HistorialMedico(models.Model):
    _name = 'sanatorio.quiroz.historial.medico'
    _description = 'Historial Médico'

    hx_familiar_id = fields.Many2one('sanatorio.quiroz.historial.familiar', string="HX Familiar")
    hx_personal_id = fields.Many2one('sanatorio.quiroz.historial.personal', string="HX Personal")
    hx_alergias_ids = fields.One2many('sanatorio.quiroz.historial.alergias', 'historial_medico_id', string="HX Alergias")
    hx_clinico_ids = fields.One2many('sanatorio.quiroz.historial.clinico', 'historial_medico_id', string="HX Clínico")
    hx_quirurgico_ids = fields.One2many('sanatorio.quiroz.historial.quirurgico', 'historial_medico_id', string="HX Quirúrgico")
    evolucion_ids = fields.One2many('sanatorio.quiroz.evolucion', 'historial_medico_id', string="Evolución")

