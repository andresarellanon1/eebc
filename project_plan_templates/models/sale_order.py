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

    @api.onchange('is_project')
    def _products_domain(self):
        self.order_line._products_project_domain(self.is_project)

    def action_confirm(self):
        self.ensure_one()
        for sale in self:
            if sale.is_project:
                sale.state == 'estimation'
            else:
                return super(SaleOrder, self).action_confirm()

    def action_create_project(self):
        self.ensure_one()
        for sale in self:
            sale.state == 'budget'

    
            