{
    "name": "Customer Sales",
    "version": "17.0.1.01",
    "depends": [
        "base",
        "sale",
        "contacts",
        "contacts_enterprise",
        "account",
        "account_accountant",
        "base_address_extended",
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
