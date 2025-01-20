{
    "name": "Customer Sales Credit",
    "version": "17.0.1.01",
    "depends": [
        "base",
        "sale",
        "sale_account_accountant",
        "contacts",
        "contacts_enterprise",
        "account_accountant",
        "base_address_extended"
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
            Campos para clientes. Se agregan campos y validaciones de credito a flujos de venta.
    """,
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
    ],
    "license": "LGPL-3",
}
