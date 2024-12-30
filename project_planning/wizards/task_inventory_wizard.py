from odoo import models, fields, api

class ProjectCreation(models.TransientModel):
    _name = 'task.inventory.wizard'
    _description = 'Wizard to confirm project creation'