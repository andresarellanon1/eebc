from odoo import fields, models, api

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    project_plan_id = fields.Many2one('project.plan', string="Project plan template")