from odoo import models, fields, api

class LineActivities(models.Model):

    _name = 'line.activities'

    name = fields.Char(string="Nombre", store=True)
    description = fields.Char(string="Descripción", store=True)
    allocated_hours = fields.Float(string="Horas", store=True)
    
    activity_template = fields.Many2one(
        'activity.template',  # Referencia al modelo
        string='Actividad',
        store = True,
        copied = True)

    project_id = fields.Many2one(
        'project.project',  # Referencia al modelo
        string='Actividad',
        store = True,
        copied = True)


    