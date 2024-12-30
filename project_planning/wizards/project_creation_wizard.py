from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'project.creation.wizard'
    _description = 'Wizard to confirm project creation'