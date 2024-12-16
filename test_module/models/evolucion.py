from odoo import models, fields, api



class Evolucion(models.Model):
    _name = 'sanatorio.quiroz.evolucion'
    _description = 'Evolución'

    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    evol_fecha = fields.Date(string="Evol Fecha")
    intervencion = fields.Selection([('consulta', 'Consulta'), ('ingreso', 'Ingreso')], string="Intervención")
    interrogatorio_id = fields.Many2one('sanatorio.quiroz.interrogatorio', string="Interrogatorio")
    motivo_ingreso = fields.Text(string="Motivo de Ingreso")
    exploracion_id = fields.Many2one('sanatorio.quiroz.exploracion', string="Exploración")
    labs_imgs_id = fields.Many2one('sanatorio.quiroz.labs.imgs', string="Labs/Imgs")
    analisis = fields.Text(string="Análisis")
    diagnostico = fields.Text(string="Diagnóstico")
    plan = fields.Text(string="Plan")
    pronostico = fields.Selection([('b', 'Bueno'), ('m', 'Malo'), ('r', 'Regular')], string="Pronóstico")
    motivo_egreso = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string="Motivo de Egreso")

