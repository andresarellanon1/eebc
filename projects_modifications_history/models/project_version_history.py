from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProjectVersionHistory(models.Model):

    _name = 'project.version.history'
    _description = 'Project Version History'
    _rec_name = 'name'  

    name = fields.Char(
        string='Nombre de Historial',
        default="Historial de Modificación", 
        required=True
    )
    project_id = fields.Many2one('project.project', string='Proyecto')
    modified_by = fields.Many2one('res.users', string='Modificado por')
    modification_motive = fields.Html(string='Motivo de los cambios')

    project_name = fields.Char(string='Nombre del proyecto')

    project_versions_lines = fields.One2many('project.version.lines','project_version_history_id', string="Versions")