{
    'name': 'Listas de precios en producto',
    'summary': 'Visor de lista de precios en productos y lineas de documentos de venta.',
    'description': """
        Este módulo muestra una tabla con la lista de precios dentro de la vista de cada producto.
        Muestra una widget de selección para la lista de precios en el documento de venta y el documento de factura de cliente.
        Actualiza el precio unitario de la línea en cuestión correspondiente con la lista de precios seleccionada en cualquiera de estos dos documentos.
    """,
    'version': '17.0.2.362',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'stock',
        'product',
        'sale_management',
        'product_email_template',
        'price_list_customer',
        'partner_branches'
    ],
    'data': [
        'views/product_pricelist_line_views.xml',
        'views/product_pricelist_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
        'security/ir.model.access.csv'
    ],
    "license": "LGPL-3",
    'installable': True
}
