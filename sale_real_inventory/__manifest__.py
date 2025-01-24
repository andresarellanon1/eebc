{
    'name': 'Inventario Real Para Ventas',
    'version': '17.0.1.003',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
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
        "weekdays"
    ],
    'data': [
        'security/ir.model.access.csv',
        "views/sale_order_line_views.xml",
    ],
    "license": "LGPL-3",
    'installable': True
}
