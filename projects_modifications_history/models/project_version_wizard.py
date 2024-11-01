from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProjectVersionWizard(models.TransientModel):

    _name = 'project.version.wizard'
    _description = 'Wizard for project version history'

    modification_date = fields.Datetime(string='Modification date')
    modification_motive = fields.Html(string='Motive of adjustment')
    modified_by = fields.Many2one('res.users', string='Modified by')
    project_plan_id = fields.Many2one('project.plan', string="Project Plan", required=True, readonly="True")
    
    project_plan_pickings = fields.Many2many(
        'project.plan.pickings', 
        string="Picking Templates"
    )

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

        history = self.env['project.version.history'].create({
            'project_id': self.project_id.id,
            'modified_by': self.modified_by.id,
            'modification_motive': self.modification_motive,
            'project_name': self.project_id.name,
        })

        self.env['project.version.lines'].create({
            'project_version_history_id': history.id,
            'modification_date': self.modification_date,
            'modified_by': self.modified_by.id,
            'modification_motive': self.modification_motive,
            'project_plan_lines': [(6, 0, self.project_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.project_picking_lines.ids)],
        })

        self.project_id.write({
            
        })

        
        return {
            'type': 'ir.actions.act_window_close'
        }