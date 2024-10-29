from odoo import api, fields, models
import json
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

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
    project_plan_lines = fields.One2many('project.plan.line', 'version_id', string='Planeación')
    project_picking_lines = fields.One2many('project.picking.lines', 'version_id', string='Stock')

    @api.model
    def create_version(self, project, user):
        version = self.create({
            'modified_by': user.name,
            'project_id': project.id,
            'motive': project.change_motive,
            'version_date': fields.Datetime.now(),
            # Datos del proyecto que se van a guardar
            'project_name': project.name,
            'description': project.description,
            'date_start': project.date_start,
        })

        # Copiar las líneas one2many con el ID de la versión creada
        plan_lines = []
        for line in project.project_plan_lines:
            plan_lines.append((0, 0, line.copy_data({'version_id': version.id})[0]))

        picking_lines = []
        for line in project.project_picking_lines:
            picking_lines.append((0, 0, line.copy_data({'version_id': version.id})[0]))

        # Realizar un write para actualizar el registro de la versión con las líneas one2many
        version.write({
            'project_plan_lines': plan_lines,
            'project_picking_lines': picking_lines,
        })

        return version