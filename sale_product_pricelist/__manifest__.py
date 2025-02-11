{
    'name': 'Listas de precios en producto',
    'summary': 'Visor de lista de precios en productos y lineas de documentos de venta.',
    'description': """
        Este módulo gestiona listas de precios en la vista de productos y documentos de venta y facturación. 
        Permite seleccionar una lista de precios y actualiza automáticamente el precio unitario según la 
        selección. Utiliza un algoritmo de prioridades para determinar la lista de precios más adecuada, 
        considerando las configuraciones del cliente y las listas personalizadas.

        También admite multi-divisa y multi-sucursal: si la orden cambia de divisa, busca una lista de precios
        equivalente; además, solo muestra listas de precios correspondientes a la sucursal del vendedor.
    """,
    'version': '17.0.4.016',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'stock',
        'product',
        'sale_management',
        'product_email_template',
        'partner_priority_pricelist',
        'currency_lock'
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
