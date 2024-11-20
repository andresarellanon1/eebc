from odoo import fields, models, api

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    project_plan_id = fields.Many2one('project.plan', string="Project plan template")
    project_id = fields.Many2one('project.project', string="Project")
    service_policy = fields.Many2one('product_template', string="Service Policy")
    service_tracking = fields.Selection(
        selection=[
            ('no', 'Nada'),
            ('task_global_project', 'Tarea'),
            ('task_in_project', 'Proyecto y tarea'),
            ('project_only', 'Proyecto'),
        ],
        string='Service Tracking',
        default='no', 
    )