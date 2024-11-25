from odoo import fields, models, api
import json

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_project = fields.Boolean(string="Is project?", default=False)
    project_name = fields.Char(string="Project title")

    state = fields.Selection(
        selection_add=[
            ('estimation', 'Estimation'),
            ('budget', 'Budget')
        ],
        ondelete={
            'estimation': 'set default',
            'budget': 'set default'
        }
    )

    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')

    def action_confirm(self):
        self.ensure_one()
        for sale in self:
            if sale.is_project:
                sale.state == 'estimation'
                plan_lines = []
                for line in order_line:
                    plan_lines.appen((0, 0, {
                        'name': line.name,
                    }))
                    for plan in line.product_id.project_plan_id:
                        plan_lines.append((0, 0, {
                            
                        }))
            else:
                return super(SaleOrder, self).action_confirm()

    def action_create_project(self):
        self.ensure_one()
        for sale in self:
            sale.state == 'budget'

    
            