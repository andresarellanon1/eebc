{
    'name': 'Conversor de divisa por líneas',
    'summary': 'Conversor de divisas por líneas individuales de documentos de venta y facturas de cliente. Usa listas de precio por línea de documento de venta.',
    'description': """
            Este módulo muestra un campo de divisa seleccionable y sobreescribe los comportamientos default de la orden de venta sobre la lista de precios.
            Requiere el uso de lista de precios por línea de documento de venta.
            Agrega una configuración para definir una ganancia en la divisa de la empresa por cada unidad de divisa convertida.
            Depende del módulo price_list_product para calcular los precios por línea.
            Es necesario crear una lista de precios en la divisa de la empresa y su Equivalente en la divisa objetivo desde la configuración base de odoo para usar la funcionalidad completa de este módulo.
    """,
    'version': '17.0.1.100',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['purchase', 'stock', 'product', 'contacts', 'price_list_product'],
    'data': [
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
        'views/inherit_sales_config_settings.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
