{
    'name': "EBBC NOTICES",
    'version': '17.0.1.26',
    'depends': ["stock"],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo es para los avisos.

    """,
    'depends': ['purchase', 'account','base'],

    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/notices_views.xml",
        "views/stock_picking_views.xml"
        
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
