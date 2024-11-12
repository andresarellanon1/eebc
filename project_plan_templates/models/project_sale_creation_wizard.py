from odoo import fields, models, api

class ProjectSaleWizard(models.TransientModel):

    _name = 'project.sale.creation.wizard'
    _description = 'Wizard to create projects from sale order'

    products_ids = fields.Many2many('product.template')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)

    def confirm_wizard(self):
        self.sale_order_id.state = 'sale'