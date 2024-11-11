from odoo import fields, models, api

class ProjectSaleWizard(models.TransientModel):

    _name = 'project.sale.creation.wizard'
    _description = 'Wizard to create projects from sale order'

    products_ids = fields.Many2many('product.template')

    