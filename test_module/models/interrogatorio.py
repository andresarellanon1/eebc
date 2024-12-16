from odoo import models, fields, api



class Interrogatorio(models.Model):
    _name = 'sanatorio.quiroz.interrogatorio'
    _description = 'Interrogatorio'

    sintoma = fields.Text(string="Síntoma")
    ss_inicio = fields.Integer(string="Inicio (días)")
    ss_localizacion = fields.Text(string="Localización")
    ss_intensidad = fields.Selection([('lo', 'Lo'), ('me', 'Me'), ('hi', 'Hi')], string="Intensidad")
    ss_irradiacion = fields.Text(string="Irradiación")
    ss_atenuantes = fields.Text(string="Atenuantes")
    ss_agravantes = fields.Text(string="Agravantes")
