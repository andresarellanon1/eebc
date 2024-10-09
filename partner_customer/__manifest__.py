{
    'name': "Partner Customer Extension",
    'version': '17.0.0.01',
    'depends': [
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
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo conforma las configuraciones de los clientes.
    """,
    "data": [
        "views/res_partner.xml",
        "views/sale_order_views.xml",
        "views/res_country_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
