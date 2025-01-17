{
    'name': "Partner Customer Extension",
    'version': '17.0.0.01',
    'depends': [
        "sale",
        "contacts",
        "contacts_enterprise",
        "base_address_extended",
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Utilidades para las implementaciones de Quadro Soluciones.
        Configuraciones y campos a los contactos.
        Computa las direcciones al cambiar el partner de las sale orders.
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
