from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProjecVersionLines(models.Model):

    _name = 'project.version.lines'
    _description = 'Project versions history'

    modification_date = fields.Datetime(string='Modification date')
    project_id = fields.Many2one('project.project', string='Project')
    modified_by = fields.Many2one('res.users', string='Modified by')
    modification_motive = fields.Html(string='Motive of adjustment')
    project_name = fields.Char(string='Project name')
    project_version_history_id = fields.Many2one('project.version.history', string="Project history")

    #Relación que obtiene los valores de el project_plan_lines en la versión actual
    project_plan_lines = fields.Many2many(
        'project.plan.line',
        string='Planeación',
        relation='project_version_lines_project_plan_line_rel' #Permite que haya más relaciones Many2many hacia project.plan.line
    )

    #Relación que obtiene los valores de el project_picking_lines en la versión actual
    project_picking_lines = fields.Many2many(
        'project.picking.lines',
        string='Stock',
        relation='project_version_lines_picking_lines_rel' #Permite que haya más relaciones Many2many hacia project.picking.lines
    )

    #Relación que obtiene los valores de el project_plan_lines en la versión anterior
    previous_version_plan_lines = fields.Many2many(
        'project.plan.line',
        string="Last version plan lines",
        relation='project_version_lines_previous_plan_line_rel' 
    )

    #Relación que obtiene los valores de el project_picking_lines en la versión anterior
    previous_version_picking_lines = fields.Many2many(
        'project.picking.lines',
        string="Last version picking lines",
        relation='project_version_lines_previous_picking_lines_rel' 
    )

    #Campo del valor del número de la versión
    version_number = fields.Char(
        string='Version Number',
        compute='_compute_version_number',
        store=True #Indica que el valor se almacena en la base de datos
    )

    #Boleano que indica si tiene versión previa
    has_previous_version = fields.Boolean(
        string="Has Previous Version",
        compute='_compute_previous_version_lines',
        store=True #Indica que el valor se almacena en la base de datos
    )

    #Método que computa el número de versión
    @api.depends('modification_date', 'project_id')
    def _compute_version_number(self):
        for record in self:
            # Check if a project_id is set for the current record
            if record.project_id:
                # Search for all project version lines associated with the current project_id
                # The search retrieves all version lines for the project, ordered by modification_date
                versions = self.env['project.version.lines'].search([('project_id', '=', record.project_id.id)], order='modification_date')
                
                # Set the version number based on the index of the current record in the found versions
                # The version number is "V" followed by the position of the current record (index + 1)
                record.version_number = f"V{versions.ids.index(record.id) + 1}" if record.id else "V0"
            else:
                # If no project_id is set, assign version number "V0"
                record.version_number = "V0"

    @api.depends('project_id')
    def _compute_previous_version_lines(self):
        for record in self:
            
            # Assign the current project's name to the project_name field of the current record
            record.project_name = record.project_id.name

            # Search for the previous version of the project (if it exists) for the specific record.
            # We search for records with the same project_id and an id smaller than the current one.
            previous_version = self.search([
                ('project_id', '=', record.project_id.id),  # Same project_id
                ('id', '<', record.id)  # Search for records with smaller ids (previous versions)
            ], order="id desc", limit=1)  # Order by id descending to get the most recent previous version

            # If a previous version is found (i.e., previous_version is not None)
            if previous_version:
                # Assign the previous version's project plan lines to the current record's previous_version_plan_lines
                record.previous_version_plan_lines = previous_version.project_plan_lines

                # Assign the previous version's project picking lines to the current record's previous_version_picking_lines
                record.previous_version_picking_lines = previous_version.project_picking_lines

                # Mark that this record has a previous version
                record.has_previous_version = True
            else:
                # If no previous version is found (no earlier project with that id exists),
                # we assign empty values to the plan and picking lines
                record.previous_version_plan_lines = [(5, 0, 0)]  # (5, 0, 0) is the syntax for clearing lines

                # Similarly, assign empty values to the picking lines
                record.previous_version_picking_lines = [(5, 0, 0)]

                # Mark that there is no previous version
                record.has_previous_version = False