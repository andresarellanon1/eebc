{
    'name': "EBBC NOTICES",
    'version': '17.0.1.09',
    'depends': ["stock"],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo es para los avisos.

    """,
    'depends': ['purchase', 'account'],

    "data": [
        "views/notices_views.xml",
        "views/menu.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
