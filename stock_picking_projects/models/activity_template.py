from odoo import models, fields, api

class ActivityTemplate(models.Model):

    _name = 'activity.template'

    name = fields.Char(string="Nombre", store=True)
    description = fields.Char(string="Descripción", store=True)

    project_id = fields.Many2one(
        'project.project',  # Referencia al modelo
        string='Actividad',
        store = True,
        copied = True)

    line_activities_ids = fields.One2many(
        'line.activities',  # Referencia al modelo
        'activity_template',     # Campo Many2one
        string='Actividades'
        )

    