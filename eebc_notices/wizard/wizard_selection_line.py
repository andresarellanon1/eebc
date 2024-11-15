from odoo import models, fields, api

class WizardSelectionLine(models.TransientModel):
    _name = 'wizard.selection.line'
    _description = 'Wizard Selection Line'

    wizard_id = fields.Many2one('select.notice.wizard', string='Wizard', required=True)
    record_id = fields.Many2one('your.model', string='Record', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)