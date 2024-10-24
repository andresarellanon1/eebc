from odoo import api, fields, models
import json
from odoo.exceptions import ValidationError

class ProjectVersion(models.Model):
    _name = 'project.version'
    _description = 'Project Version History'

    project_id = fields.Many2one('project.project', string='Project')
    version_date = fields.Date(string='Modification date')
    modified_by = fields.Char(string='Modified by')
    project_name = fields.Char(string='Project name')
    motive = fields.Char(string='Motive of adjustment')

    @api.model
    def create_version(self, project):
        project_data = {
            # Datos del proyecto que se van a guardar
            'name': project.name,
            'description': project.description,
            'date_start': project.date_start,
            'date': project.date,
            'site_supervisor': project.site_supervisor_id,

        }

        # Guardamos los datos del proyecto en formato JSON para hacer una "snapshot"
        self.create({
            'project_id': project.id,
            'data_snapshot': json.dumps(project_data),
            'version_date': fields.Datetime.now(),
        })