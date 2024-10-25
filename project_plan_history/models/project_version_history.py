from odoo import api, fields, models
import json
from odoo.exceptions import ValidationError

class ProjectVersion(models.Model):
    _name = 'project.version'
    _description = 'Project Version History'

    project_id = fields.Many2one('project.project', string='Project')
    
    version_date = fields.Date(string='Version date')
    modified_by = fields.Char(string='Modified by')
    motive = fields.Char(string='Motive of adjustment')

    project_name = fields.Char(string='Project name')
    description = fields.Text(string='Description')
    date_start = fields.Date(string='Start date')

    # project_plan_lines = fields.One2many('project.plan.line', 'version_id', string='Planeación')
    # project_picking_lines = fields.One2many('project.project', 'version_id', string='Stock')
    project_ids = fields.One2many('project.project', 'version_id', string='Historial')
    @api.model
    def create_version(self, project, user):
        # Guardamos los datos del proyecto
        self.create({
            'modified_by': user.name,
            'project_id': project.id,
            'version_date': fields.Datetime.now(),
            # Datos del proyecto que se van a guardar
            'project_name': project.name,
            'description': project.description,
            'date_start': project.date_start,
            'project_ids': [(0, 0, {
                'name': line.name,
            }) for line in project.child_ids],
        })