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

    @api.depends('modification_date')
    def _compute_version_number(self):
        for record in self:
            record.version_number = f"V{record.id}" if record.id else "V0"

    @api.depends('project_id')
    def _compute_previous_version_lines(self):
        for record in self:
            record.project_name = record.project_id.project_name

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