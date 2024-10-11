from odoo import models, fields, api

class ActivityTemplate(models.Model):

    _name = 'activity.template'

    name = fields.Char(string="Nombre", store=True)
    description = fields.Char(string="Descripción", store=True)
    allocated_hours = fields.Float(string="Horas", store=True)
    date_start = fields.Date(string="Fecha planeada", store=True)

    project_id = fields.Many2one(
        'project.project',  # Referencia al modelo
        string='Actividad',
        store = True,
        copied = True)

    