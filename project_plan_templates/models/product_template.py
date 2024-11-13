from odoo import fields, models, api

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    project_plan_id = fields.Many2one('project.plan', string="Project plan template")

    def action_create_project(self):
        self.ensure_one()

        project_plan = self.project_plan_id

        return {
            'name': 'Create Project',
            'view_mode': 'form',
            'res_model': 'project.creation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_plan_id': project_plan,
                'default_project_plan_lines': [(6, 0, project_plan.project_plan_lines.ids)],
                'default_project_plan_pickings': [(6, 0, project_plan.project_plan_pickings.ids)],
                'default_picking_lines': [(6, 0, project_plan.picking_lines.ids)],
                'default_description': project_plan.description,
                'default_is_sale_order': True,
            }
        }