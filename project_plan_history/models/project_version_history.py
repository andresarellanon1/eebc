from odoo import api, fields, models
import datetime, re
from odoo.exceptions import ValidationError
from datetime import datetime

class ProjectVersion(models.Model):
    _name = 'project.version'

    modification_date = fields.Date(string='Modification date')
    modified_by = fields.Char(string='Modified by')
    project_name = fields.Char(string='Project name')
    motive = fields.Char(string='Motive of adjustment')