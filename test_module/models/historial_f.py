from odoo import models, fields, api



class HistorialFamiliar(models.Model):
    _name = 'sanatorio.quiroz.historial.familiar'
    _description = 'Historial Familiar'

    relacion = fields.Selection([
        ('padre', 'Padre'), ('madre', 'Madre'), ('hermano', 'Hermano'), ('hermana', 'Hermana'), ('otro', 'Otro')
    ], string="Relación")
    edad_familiar = fields.Integer(string="Edad del Familiar")
    vive = fields.Selection([('si', 'Sí'), ('no', 'No')], string="¿Vive?")
    relacion_hereditaria = fields.Text(string="Relación Hereditaria")

