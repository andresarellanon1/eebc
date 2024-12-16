from odoo import models, fields, api



class Exploracion(models.Model):
    _name = 'sanatorio.quiroz.exploracion'
    _description = 'Exploración'

    signos_vitales_id = fields.Many2one('sanatorio.quiroz.signos.vitales', string="Signos Vitales")
    region_anatomica = fields.Selection([
        ('cc', 'Cabeza y Cuello'), ('tx', 'Tórax'), ('ab', 'Abdomen'), ('gn', 'Genitales'), ('br', 'Brazos'), ('lg', 'Piernas')
    ], string="Región Anatómica")
    hallazgo = fields.Text(string="Hallazgo")

