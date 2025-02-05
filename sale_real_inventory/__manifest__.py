{
    'name': 'Inventario Real Para Ventas',
    "summary": "Calcula la cantidad disponible de productos en las órdenes de venta.",
    "description": """
        El módulo "Inventario Real Para Ventas" calcula y muestra la cantidad real disponible de un producto en las líneas de las órdenes de venta, 
        teniendo en cuenta las reservas y el stock real en el almacén correspondiente.
    """,
    'version': '17.0.1.004',
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
