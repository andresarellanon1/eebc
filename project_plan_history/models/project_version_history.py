from odoo import api, fields, models

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
            'version_date': fields.Datetime.now(),
            'project_name': project.name,
            'description': project.description,
            'date_start': project.date_start,
        })

        plan_line_ids = []
        for line in project.project_plan_lines:
            partner_id = line.partner_id.id if line.partner_id else False
            new_line = self.env['project.plan.line'].create({
                'version_id': version.id,
                'name': getattr(line, 'name', ''),
                'chapter': getattr(line, 'chapter', ''),
                'use_project_task': getattr(line, 'use_project_task', ''),
                'planned_date_begin': getattr(line, 'planned_date_begin', False),
                'planned_date_end': getattr(line, 'planned_date_end', False),
                'partner_id': partner_id,
                'stage_id': getattr(line.stage_id, 'id', False),
            })
            plan_line_ids.append(new_line.id)

        picking_line_ids = []
        for line in project.project_picking_lines:
            new_line = self.env['project.picking.lines'].create({
                'version_id': version.id,
                'quantity': getattr(line, 'quantity', 0),
                'location_id': getattr(line.location_id, 'id', False),
            })
            picking_line_ids.append(new_line.id)

        version.write({
            'project_plan_lines': [(6, 0, plan_line_ids)],
            'project_picking_lines': [(6, 0, picking_line_ids)],
        })

        return version