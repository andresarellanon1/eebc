
from odoo import models, fields, api



class Paciente(models.Model):
    _name = 'sanatorio.quiroz.paciente'
    _description = 'Paciente'


    nombre = fields.Char(string="Nombre")
    apellido_paterno = fields.Char(string="Apellido Paterno")
    apellido_materno = fields.Char(string="Apellido Materno")
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento")
    edad = fields.Integer(string="Edad", compute="_compute_edad", store=True)
    sexo = fields.Selection([('masculino', 'Masculino'), ('femenino', 'Femenino')], string="Sexo")
    contacto_id = fields.Many2one('res.partner', string="Contacto")
    historial_medico_id = fields.Many2one('sanatorio.quiroz.historial.medico', string="Historial Médico")
    historial_administrativo_id = fields.Many2one('sanatorio.quiroz.historial.administrativo', string="Historial Administrativo")

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        for record in self:
            if record.fecha_nacimiento:
                today = fields.Date.today()
                record.edad = today.year - record.fecha_nacimiento.year - ((today.month, today.day) < (record.fecha_nacimiento.month, record.fecha_nacimiento.day))

