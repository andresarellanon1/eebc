{
    'name': "Purchase Order Type",
    'version': '17.0.1.001',
    'depends': [
        "purchase_stock"
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este módulo agrega la posibilidad de cambiar el tipo de operación de una purchase.order directamente desde la orden no confirmada.
        Esto permite un bypass de las rutas y debe usarse como un auxiliar para automatizar las entradas de inventario directamente a sus ubicaciones designadas por decisión operativa, sin necesidad de realizar primero una entrada y luego un traspaso interno.
        Este módulo puede catalogarse como QoL (Quality of Life).
    """,
    "data": [
        # "security/res.groups.xml",
        # "security/ir.model.access.csv",
        # "views/purchase_order_type.xml",
        # "views/inherit_views.xml"
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
