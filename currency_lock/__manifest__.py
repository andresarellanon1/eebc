{
    'name': 'Divisa Objetivo',
    'summary': 'Permite configurar una divisa objetivo (target_currency_id) para posterior uso en conversiones de divisa especifica entre divisa de la empresa.',
    'description': """
        El objetivo del modulo es permitir la persistencia de un campo configurable de divisa secundaria para la empresa.
        El campo se configura a nivel de empresa y se hereda a todos los documentos (sale.order & purchase.order) y sus lineas.
        Computa el ratio de conversion al seleccionar una divisa distinta a la de la empresa para los documentos compra/venta y facturas de compra/venta.
    """,
    'version': '17.0.3.007',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['base', 'product', 'purchase', 'sale', 'account', 'account_accountant'],
    'data': [
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/res_config_settings.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
