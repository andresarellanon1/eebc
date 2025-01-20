{
    "name": "Customer Sales",
    "version": "17.0.2.671",
    "depends": [
        "base",
        "sale",
        "sale_stock",
        "sale_stock_margin",
        "contacts",
        "contacts_enterprise",
        "account_accountant",
        "stock",
        "stock_account",
        "base_address_extended",
        "price_list_product",
        "weekdays"
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
            Campos para clientes.
            Funcionalidad minima y validaciones varias.
    """,
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
    ],
    "license": "LGPL-3",
}
