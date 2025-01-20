{
    'name': 'Divisa Objetivo',
    'summary': 'Permite configurar una divisa objetivo (locked_currency_id) para posterior uso en conversiones de divisa especifica entre divisa de la empresa.',
    'description': """
        El objetivo del modulo es permitir la persistencia de un campo configurable de divisa secundaria para la empresa.
        El campo se configura a nivel de empresa y se hereda a todos los documentos (sale.order & purchase.order) y sus lineas.
        Computa el ratio de conversion al seleccionar una divisa distinta a la de la empresa para los documentos compra/venta y facturas de compra/venta.
    """,
    'version': '17.0.1.999',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['base', 'purchase', 'sale', 'account', 'account_accountant'],
    'data': [
        # 'views/account_move_views.xml',
        # 'views/purchase_order_views.xml',
        # 'views/sale_order_views.xml',
        # 'views/sale_order_line_views.xml',
        # 'views/inherit_sales_config_settings.xml',
        # 'views/inherit_product_pricelist_view.xml'
    ],
    "license": "LGPL-3",
    'installable': True
}
