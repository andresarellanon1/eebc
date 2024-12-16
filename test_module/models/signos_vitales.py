from odoo import models, fields, api



class SignosVitales(models.Model):
    _name = 'sanatorio.quiroz.signos.vitales'
    _description = 'Signos Vitales'

    ta = fields.Integer(string="TA (mmHg)")
    fc = fields.Integer(string="FC (lpm)")
    fr = fields.Integer(string="FR (rpm)")
    spo2 = fields.Integer(string="SpO2 (%)")
    temp = fields.Integer(string="Temperatura (°C)")
    eva = fields.Integer(string="EVA (0-10)")
    glasgow = fields.Integer(string="GLASGOW (3-15)")
    peso = fields.Integer(string="Peso (kg)")
    talla = fields.Float(string="Talla (m)")
    imc = fields.Float(string="IMC")

