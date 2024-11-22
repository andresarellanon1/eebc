{
    'name': "Purchase Order Projects",
    'version': '17.0.0.02',
    'depends': [
        "base",
        "eebc_settings",
        "purchase_stock",
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo conforma las configuraciones de las ordenes de compra.
    """,
    "data": [
        "views/inherit_views.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
