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
            # 'motive': project.change_motive,
            'version_date': fields.Datetime.now(),
            # Datos del proyecto que se van a guardar
            'project_name': project.name,
            'description': project.description,
            'date_start': project.date_start,
        })

        # Realizar commit para asegurarnos de que la versión esté guardada
        self.env.cr.commit()

        # Crear manualmente las líneas one2many
        plan_lines = []
        for line in project.project_plan_lines:
            new_line_data = line.copy_data({'version_id': version.id})[0]
            new_line = self.env['project.plan.line'].create(new_line_data)
            plan_lines.append(new_line.id)

        picking_lines = []
        for line in project.project_picking_lines:
            new_line_data = line.copy_data({'version_id': version.id})[0]
            new_line = self.env['project.picking.lines'].create(new_line_data)
            picking_lines.append(new_line.id)

        # Refrescar la caché del registro para que aparezcan los datos en la vista
        version.invalidate_cache(['project_plan_lines', 'project_picking_lines'])

        return version