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

    @api.depends('modification_date')
    def _compute_version_number(self):
        for record in self:
            record.version_number = f"V{record.id}" if record.id else "V0"