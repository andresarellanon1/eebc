from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    branch_id = fields.Many2one('res.branch', string='Branch', store=True,
        help='Leave this field empty if this product is shared between all branches'
    )

    allowed_branch_ids = fields.Many2one('res.branch', store=True,
        string='Allowed branches',
        
    )

    branch_price = fields.Float(default=0.0, string="Precio en sucursal", store=True)

    @api.depends('company_id')
    def _compute_allowed_branch_ids(self):
        for po in self:
            po.allowed_branch_ids = self.env.user.branch_ids.ids

    branch_price_ids = fields.One2many(
        'product.branch.price', 'product_id',
        string='Branch Prices'
    )

    @api.depends('company_id')
    def _compute_branch_price(self):
        for po in self:
            _logger.warning(f'Entro al depends')
            if self.env.user.branch_id:
                po.branch_price = self.get_branch_price(self.env.user.branch_id.id)
                _logger.warning(f'Precio de la sucursal: {self.get_branch_price(self.env.user.branch_id.id)}')
            else:
                po.branch_price = 0.0

    def get_branch_price(self, branch_id):
        """Get the standard price of the product for a specific branch."""
        branch_price = self.env['product.branch.price'].search([
            ('product_id', '=', self.id),
            ('branch_id', '=', branch_id)
        ], limit=1)
        return branch_price.branch_price if branch_price else 0.0

    def write(self, vals):
        branch_id = self.env.user.branch_id.id

        if 'branch_price' in vals and branch_id:
            for product in self:
                # Buscar si ya existe un registro de precio para el producto y la sucursal
                price = self.env['product.branch.price'].search([
                    ('product_id', '=', product.id),
                    ('branch_id', '=', branch_id)
                ], limit=1)

                if price:
                    # Actualizar el precio existente
                    price.write({'branch_price': vals['branch_price']})
                    _logger.warning(f"Actualizando precio existente: {price.branch_price} para producto {product.id} en sucursal {branch_id}")
                else:
                    # Crear un nuevo registro de precio
                    price = self.env['product.branch.price'].create({
                        'branch_id': branch_id,
                        'product_id': product.id,
                        'branch_price': vals['branch_price'],
                    })
                    _logger.warning(f"Creando nuevo precio: {price.branch_price} para producto {product.id} en sucursal {branch_id}")
        
        return super(ProductTemplate, self).write(vals)