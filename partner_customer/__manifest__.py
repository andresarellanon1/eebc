{
    'name': "Partner Customer Extension",
    'version': '17.0.3.002',
    'depends': [
        "sale",
        "contacts"
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Utilidades para las implementaciones de Quadro Soluciones.
        Configuraciones y campos a los contactos de clientes.
        Computa las direcciones al cambiar el partner de las sale orders.
    """,
    "data": [
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
