from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProjectVersionWizard(models.TransientModel):

    _name = 'project.version.wizard'
    _description = 'Wizard for project version history'

    modification_date = fields.Datetime(string='Modification date')
    modification_motive = fields.Html(string='Motive of adjustment')
    modified_by = fields.Many2one('res.users', string='Modified by')
    
    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación'
    )
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock'
    )

    project_id = fields.Many2one('project.project', string='Project', required=True)

    def action_confirm_version_history(self):
        self.ensure_one()

        project = self.env['project.project'].browse(self.project_id.id)
        project.write({

        })

        existing_history = self.env['project.version.history'].search([
            ('project_id', '=', self.project_id.id)
        ], limit=1)

        if not existing_history:
            history = self.env['project.version.history'].create({
                'project_id': self.project_id.id,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
                'project_name': self.project_id.name,
            })
        else:
            history = existing_history

        for line in self.project_plan_lines:
            self.env['project.version.lines'].create({
                'project_version_history_id': history.id,
                'project_plan_line_id': line.id,
                'modification_date': self.modification_date,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
            })

        for line in self.project_picking_lines:
            self.env['project.version.lines'].create({
                'project_version_history_id': history.id,
                'project_picking_line_id': line.id,
                'modification_date': self.modification_date,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
            })

        return {
            'type': 'ir.actions.act_window_close'
        }