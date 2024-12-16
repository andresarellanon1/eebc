from odoo import models, fields, api



class HistorialPersonal(models.Model):
    _name = 'sanatorio.quiroz.historial.personal'
    _description = 'Historial Personal'

    religion = fields.Selection([
        ('catolica', 'Católica'), ('protestante', 'Protestante'), ('otra', 'Otra')
    ], string="Religión")
    escolaridad = fields.Selection([
        ('primaria', 'Primaria'), ('secundaria', 'Secundaria'), ('universidad', 'Universidad')
    ], string="Escolaridad")
    ocupacion = fields.Text(string="Ocupación")
    dieta = fields.Text(string="Dieta")
    actividad_fisica = fields.Text(string="Actividad Física")
    higiene_personal = fields.Text(string="Higiene Personal")

