{
    'name': 'Ultimo precio de proveedor',
    'summary': 'Implementa funcionalidad de proveedor principal y calcula ultimos precios de proveedores apartir de documentos de compra.',
    'description': """
            Este módulo muestra campos extra para configuración de proveedores en el inventario.
            Agrega funcionalidad para calcular los últimos precios de compra cuando se agregan líneas de orden de compra para un producto.

            Incluye funcionalidad para calcular costo de inventario de productos usando el día del "costos destino" sí existe,
            con el objetivo de cuadrar con las conversiones de capas de valoracion de inventarios.
    """,
    'version': '17.0.2.12',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['purchase', 'stock', 'product', 'contacts', 'landing_date_draft'],
    'data': [
        'views/product_supplierinfo_views.xml',
        'views/product_supplierinfo_history_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'security/ir.model.access.csv',
    ],
    "license": "LGPL-3",
    'installable': True
}
