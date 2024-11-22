{
    'name': "Purchase Order Projects",
    'version': '17.0.0.04',
    'depends': [
        "eebc_settings",
        "purchase_order_type",
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
