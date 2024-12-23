from odoo import fields, models, api

class ProjectPickingWizardLine(models.TransientModel):
    _name = 'project.picking.wizard.line'
    _description = 'Porject picking wizard lines'