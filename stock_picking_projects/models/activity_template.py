from odoo import models, fields, api

class ActivityTemplate(models.Model):

    _name = 'activity.template'

    name = fields.Char(string="Nombre", store=True)
    description = fields.Char(string="Descripción", store=True)

    project_id = fields.One2many(
        'project.project',  # Referencia al modelo
        'activities_tmpl_id',
        string='Actividad',
        )

    line_activities_ids = fields.One2many(
        'line.activities',  # Referencia al modelo
        'activity_template',     # Campo Many2one
        string='Actividades'
        )

    