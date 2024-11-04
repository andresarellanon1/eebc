from odoo import fields, models, api

class ProjecVersionLines(models.Model):

    _name = 'project.version.lines'
    _description = 'Project versions history'

    modification_date = fields.Datetime(string='Modification date')
    project_id = fields.Many2one('project.project', string='Project')
    modified_by = fields.Many2one('res.users', string='Modified by')
    modification_motive = fields.Html(string='Motive of adjustment')
    project_name = fields.Char(string='Project name')
    project_version_history_id = fields.Many2one('project.version.history', string="Project history")

    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación',
        relation='project_version_lines_project_plan_line_rel'
    )
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock',
        relation='project_version_lines_picking_lines_rel'
    )

    previous_version_plan_lines = fields.Many2many(
        'project.plan.line',
        string="Last version plan lines",
        relation='project_version_lines_previous_plan_line_rel'
    )

    previous_version_picking_lines = fields.Many2many(
        'project.picking.lines',
        string="Last version picking lines",
        relation='project_version_lines_previous_picking_lines_rel'
    )

    version_number = fields.Char(
        string='Version Number',
        compute='_compute_version_number',
        store=True
    )

    has_previous_version = fields.Boolean(
        string="Has Previous Version",
        compute='_compute_previous_version_lines',
        store=True
    )

    # This method generates a version number for the project's change history.
    # The version number is computed based on the record's ID, prefixed with "V".
    # If the record has an ID, the version number is set as "V<record.id>";
    # otherwise, it defaults to "V0".

    @api.depends('modification_date')
    def _compute_version_number(self):
        for record in self:
            record.version_number = f"V{record.id}" if record.id else "V0"

    # This method retrieves the task lines and inventory lines from the version
    # immediately preceding the selected version, allowing for comparison between
    # the selected version and the previous one.
    # It sets the project name based on the related project and searches for the most recent
    # version with a lower ID within the same project.
    # If a previous version is found:
    # - It assigns the previous version's task and inventory lines to the respective fields.
    # - It combines the selected version's lines with those from the previous version.
    # - It marks that there is a previous version available.
    # If no previous version is found:
    # - It clears the previous version’s task and inventory lines.
    # - It marks that there is no previous version.

    @api.depends('project_id')
    def _compute_previous_version_lines(self):
        for record in self:
            record.project_name = record.project_id.name

            previous_version = self.search([
                ('project_id', '=', record.project_id.id),
                ('id', '<', record.id)
            ], order="id desc", limit=1)

            if previous_version:
                record.previous_version_plan_lines = previous_version.project_plan_lines
                record.previous_version_picking_lines = previous_version.project_picking_lines
                
                record.project_plan_lines = record.project_plan_lines | previous_version.project_plan_lines
                record.project_picking_lines = record.project_picking_lines | previous_version.project_picking_lines
                
                record.has_previous_version = True
            else:
                record.previous_version_plan_lines = [(5, 0, 0)]
                record.previous_version_picking_lines = [(5, 0, 0)]
                record.has_previous_version = False