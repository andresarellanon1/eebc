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
            'name': 'Crear Nueva Tarea',
            'view_mode': 'form',
            'res_model': 'project.task.create.wizard',
            'target': 'new',  # Abre la vista en un pop-up
            'context': {
                'default_project_id': self.id,  # Asigna el proyecto actual en el wizard
            }
        }