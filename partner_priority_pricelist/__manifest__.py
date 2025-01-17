{
    'name': 'Listas de precios en contactos',
    'summary': 'Visor de lista de precios en contactos.',
    'description': """
        Este módulo muestra una tabla con los niveles de listas de precios dentro de la vista de cada cliente filtrado por la divisa del cliente.
        Este módulo agrega una divisa de cliente.
        Este módulo carga por defecto la divisa y la lista de precios del cliente cuando se selecciona para el campo 'partner_id' de un documento de venta 'sale_order'.
    """,
    'version': '17.0.1.06',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/product_pricelist_views.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
