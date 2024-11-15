from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectVersionWizard(models.TransientModel):

    _name = 'project.version.wizard'
    _description = 'Wizard for project version history'

    modification_date = fields.Datetime(string='Modification date')
    modification_motive = fields.Html(string='Motive of adjustment')
    modified_by = fields.Many2one('res.users', string='Modified by', required=True)

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación'
    )
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock'
    )

    project_id = fields.Many2one('project.project', string='Project', required=True)

    # This action confirms and records changes in the project's version history.
    # It ensures the existence of a project version history, creates one if none exists, 
    # validates that a modification reason is provided, and raises an error if it's missing.
    # The method generates tasks for the project using `create_project_tasks` from the `project.project` model.
    # Afterward, it creates a new entry in the version history with the current modification details.
    # Finally, it saves the updated project information and closes the wizard window.

    def action_confirm_version_history(self):
        self.ensure_one()  # Ensure that only one record is being processed.

        project = self.env['project.project'].browse(self.project_id.id)  # Fetch the project by its ID.

        # Check if a version history already exists for the current project.
        existing_history = self.env['project.version.history'].search([
            ('project_id', '=', self.project_id.id)
        ], limit=1)

        # If no version history exists, create a new one.
        if not existing_history:
            history = self.env['project.version.history'].create({
                'project_id': self.project_id.id,
                'modified_by': self.modified_by.id,
                'modification_motive': self.modification_motive,
                'project_name': self.project_id.name,
            })
        else:
            history = existing_history  # Use the existing history if found.

        # Ensure that a modification motive is provided; raise an error if missing.
        if not self.modification_motive:
            raise UserError(f'Hace falta agregar el motivo de la modificacion.')

        # Create any newly added tasks for the project.
        project.create_project_tasks()

        # Create a new entry in the project version lines for the modification details.
        self.env['project.version.lines'].create({
            'project_version_history_id': history.id,
            'modification_date': self.modification_date,
            'modified_by': self.modified_by.id,
            'modification_motive': self.modification_motive,
            'project_plan_lines': [(6, 0, self.project_plan_lines.ids)],
            'project_picking_lines': [(6, 0, self.project_picking_lines.ids)],
        })

        # Save the updated project information (though no specific changes are made here).
        project.write({})

        # Close the wizard window after completing the action.
        return {
            'type': 'ir.actions.act_window_close'
        }