{
    'name': "Purchase Order Type",
    'version': '17.0.0.18',
    'depends': [
        "purchase_stock"
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo conforma las configuraciones de las ordenes de compra.
    """,
    "data": [
        "security/res.groups.xml",
        "security/ir.model.access.csv",
        "data/purchase_type_order_data.xml",
        "views/purchase_order_type.xml",
        "views/inherit_views.xml"
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
