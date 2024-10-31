from odoo import fields, api, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_plan_id = fields.Many2one('project.plan', string="Project template", readonly="True")
    project_plan_lines = fields.One2many('project.plan.line', 'origin_project_id', string="Project plan lines")
    project_picking_ids = fields.Many2many('project.plan.pickings', string="Stock picking")
    project_picking_lines = fields.One2many('project.picking.lines', 'project_id', string="Project picking lines")

    def action_create_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Tarea',
            'view_mode': 'form',
            'res_model': 'project.task',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'create_from_project': True
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('create_from_project'):
                task_name = vals.get('name')
                project_id = vals.get('project_id')

                if self.env['project.task'].search_count([
                    ('name', '=', task_name),
                    ('project_id', '=', project_id)
                ]):
                    raise ValidationError("Esa tarea ya existe en este proyecto")

        return super().create(vals_list)