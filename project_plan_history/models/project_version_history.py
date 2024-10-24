from odoo import api, fields, models
import json
from odoo.exceptions import ValidationError

class ProjectVersion(models.Model):
    _name = 'project.version'
    _description = 'Project Version History'

    project_id = fields.Many2one('project.project', string='Project')
    version_date = fields.Date(string='Version date')
    modified_by = fields.Char(string='Modified by')
    project_name = fields.Char(string='Project name')
    motive = fields.Char(string='Motive of adjustment')

    @api.model
    def create_version(self, project, user):
        # Guardamos los datos del proyecto
        self.create({
            'modified_by': user.name,
            'project_id': project.id,
            'version_date': fields.Datetime.now(),
            # Datos del proyecto que se van a guardar
            'name': project.name,
            'description': project.description,
            'date_start': project.date_start,
            'date': project.date,
            'site_supervisor': project.site_supervisor_id,
        })