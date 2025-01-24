from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    supplier_history = fields.One2many(
        "product.supplierinfo_history",
        "product_template_id",
        string="Historial de proveedores",
        help="Historial de relación proveedor-compra para este producto",
        readonly=True
    )

    # === Main Supplier === #
    main_supplier_id = fields.Many2one(
        "product.supplierinfo",
        string="Proveedor principal",
        help='Se selecciona desde el registro de proveedor.',
        compute="_compute_main_supplier_id",
        store=True,
        readonly=True,
    )

    main_supplier_last_price = fields.Float(
        string="Último costo proveedor principal",
        help="Se computa desde el registro de proveedor.\n"
        "Cuando la divisa es diferente a la del costo base,\n"
        "se utiliza este campo para re-computar el costo base al tipo de cambio del dia en curso.",
        digits="Product Price",
        store=False,
        readonly=True,
        compute="_compute_main_supplier_last_price",
    )

    main_supplier_last_order_currency_id = fields.Many2one(
        string="Divisa proveedor principal",
        help='Se computa desde el registro de proveedor.',
        comodel_name='res.currency',
        compute="_compute_main_supplier_last_order_currency_id",
        store=False,
        readonly=True
    )

    # === Last Supplier === #
    last_supplier_id = fields.Many2one(
        "product.supplierinfo",
        string="Ultimo proveedor",
        help='Se computa desde el historial de proveedores.',
        compute="_compute_last_supplier_id",
        store=True,
        readonly=True,
    )
    last_supplier_last_price = fields.Float(
        string="Último costo del ultimo proveedor",
        help='Se computa desde el registro de proveedor. Es el ultimo precio del proveedor mas reciente, no necesariamente el principal.',
        compute="_compute_last_supplier_last_price",
        digits="Product Price",
        store=True,
        readonly=True,
    )
    last_supplier_datetime = fields.Datetime(string="Fecha ultimo proveedor", readonly=True, compute="_compute_last_supplier_datetime")
    last_supplier_last_order_currency_id = fields.Many2one(
        string="Divisa del ultimo proveedor",
        help='Se computa desde el registro de proveedor.',
        comodel_name='res.currency',
        compute="_compute_last_supplier_last_order_currency_id",
        store=True,
        readonly=True
    )

    @api.depends("seller_ids", "seller_ids.is_main_supplier")
    def _compute_main_supplier_id(self):
        for template in self:
            if template.seller_ids:
                template.main_supplier_id = template.seller_ids.filtered(
                    lambda s: s.is_main_supplier
                )[:1]
            else:
                template.main_supplier_id = False

    @api.depends("seller_ids", "main_supplier_id.price")
    def _compute_main_supplier_last_price(self):
        for template in self:
            if template.main_supplier_id:
                template.main_supplier_last_price = template.main_supplier_id.price
            else:
                template.main_supplier_last_price = 0.00

    @api.depends("seller_ids", "main_supplier_id.currency_id")
    def _compute_main_supplier_last_order_currency_id(self):
        for template in self:
            if template.main_supplier_id:
                template.main_supplier_last_order_currency_id = template.main_supplier_id.currency_id
            else:
                template.main_supplier_last_order_currency_id = False

    @api.depends("seller_ids", "supplier_history")
    def _compute_last_supplier_id(self):
        for template in self:
            if template.supplier_history:
                sorted_history = template.supplier_history.sorted(key=lambda r: r.datetime, reverse=True)
                template.last_supplier_id = sorted_history[0].product_supplierinfo_id
            else:
                template.last_supplier_id = False

    @api.depends("seller_ids", "supplier_history")
    def _compute_last_supplier_datetime(self):
        for template in self:
            template.last_supplier_datetime = False
            if template.supplier_history:
                sorted_history = template.supplier_history.sorted(key=lambda r: r.datetime, reverse=True)
                if sorted_history[0].datetime:
                    template.last_supplier_datetime = sorted_history[0].datetime
                else:
                    template.last_supplier_datetime = False

    @api.depends("seller_ids", "last_supplier_id.price")
    def _compute_last_supplier_last_price(self):
        for template in self:
            if template.last_supplier_id:
                template.last_supplier_last_price = template.last_supplier_id.price
            else:
                template.last_supplier_last_price = False

    @api.depends("seller_ids", "last_supplier_id.currency_id")
    def _compute_last_supplier_last_order_currency_id(self):
        for template in self:
            if template.last_supplier_id:
                template.last_supplier_last_order_currency_id = template.last_supplier_id.currency_id
            else:
                template.last_supplier_last_order_currency_id = False
