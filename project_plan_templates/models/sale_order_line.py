from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    products_project_domain = fields.Many2many('product.template', store=True, compute="_products_project_domain")
    code = fields.Char(string="Code")
    
    project_plan_lines = fields.One2many('project.plan.line', 'sale_order_id')
    for_modification = fields.Boolean(string="For modification", default=True)
    last_service_price = fields.Float(string="Ultimo precio del servicio")
    is_modificated = fields.Boolean(string="Is modificated", default=False)
    not_modificable = fields.Boolean(default=False)

    @api.depends('order_id', 'order_id.is_project')
    def _products_project_domain(self):
        """
        Calcula el dominio de productos disponibles en función de si la orden está asociada a un proyecto.
        Si la orden es un proyecto, solo se muestran servicios que tienen una plantilla de planificación asociada.
        Si no es un proyecto, se muestran productos que no son servicios y están disponibles para venta.
        """
        for record in self:
            if record.order_id.is_project:
                # Buscar productos que son servicios, tienen una plantilla de planificación y están disponibles para venta
                products = self.env['product.template'].search([
                    ('detailed_type', '=', 'service'),  # Solo servicios
                    ('project_plan_id', '!=', False),  # Con plantilla de planificación
                    ('sale_ok', '=', True),  # Disponibles para venta
                ])
                record.products_project_domain = [(6, 0, products.ids)]  # Asignar el dominio de productos
            else:
                # Buscar productos que no son servicios y están disponibles para venta
                products = self.env['product.template'].search([
                    ('sale_ok', '=', True),  # Disponibles para venta
                    ('detailed_type', '!=', 'service'),  # Excluir servicios
                ])
                record.products_project_domain = [(6, 0, products.ids)]  # Asignar el dominio de productos


    is_long_name = fields.Boolean(string="Nombre Largo", compute="_compute_is_long_name")


    def _compute_is_long_name(self):
        """
        Calcula si el nombre del producto es largo (más de 9 caracteres).
        Este campo booleano se usa para controlar la visualización o el formato en la interfaz.
        """
        for line in self:
            line.is_long_name = line.name and len(line.name) > 9  # Verifica si el nombre tiene más de 9 caracteres
