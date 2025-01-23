from odoo import _, api, fields, models, tools


class SupplierInfoHistory(models.Model):
    _name = 'product.supplierinfo_history'
    _description = 'Historial de compras para producto y proveedor'

    datetime = fields.Datetime(string="Fecha y hora", readonly=True)
    price_unit = fields.Float(string="Precio unitario", digits="Product Price", readonly=True)

    currency_id = fields.Many2one(
        'res.currency',
        string="Divisa",
        readonly=True
    )

    order_id = fields.Many2one(
        "purchase.order",
        string="Orden",
        readonly=True
    )

    product_template_id = fields.Many2one(
        "product.template",
        string="Plantilla de producto",
        readonly=True
    )

    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        readonly=True
    )

    product_supplierinfo_id = fields.Many2one(
        "product.supplierinfo",
        string="Proveedor",
        readonly=True
    )

    landed_cost = fields.Many2one(
        "stock.landed.cost",
        string="Pedimento",
        readonly=True
    )
