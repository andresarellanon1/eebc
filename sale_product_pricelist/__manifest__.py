{
    'name': 'Listas de precios en producto',
    'summary': 'Visor de lista de precios en productos y lineas de documentos de venta.',
    'description': """
        Este módulo muestra una tabla con la lista de precios dentro de la vista de cada producto.
        Muestra una widget de selección para la lista de precios en el documento de venta y el documento de factura de cliente.
        Actualiza el precio unitario de la línea en cuestión correspondiente con la lista de precios seleccionada en cualquiera de estos dos documentos.
        Multisucursal.
    """,
    'version': '17.0.3.001',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'stock',
        'product',
        'sale_management',
        'product_email_template',
        'partner_priority_pricelist'
        # todo: agregar moudlo de  contabilidad mexicana para depender del campod unspsc
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist.xml',
        'views/product_pricelist_line.xml',
        'views/product_template.xml',
        'views/sale_order_line.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
