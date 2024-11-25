from odoo import fields, models, api

class SaleOrderLine(models.Model):
    #TODO Agregar metodo compute para el dominio de los productos

    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', store=True)
    code = fields.Char(string="Code")