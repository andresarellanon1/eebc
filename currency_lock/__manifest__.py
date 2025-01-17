{
    'name': 'Divisa Objetivo',
    'summary': 'Permite configurar una divisa objetivo (locked_currency_id) para posterior uso en conversiones de divisa especifica entre divisa de la empresa.',
    'description': """
        El objetivo del modulo es permitir la persistencia de un campo configurable de divisa secundaria para la empresa.
        El campo se configura a nivel de empresa y se hereda a todos los documentos (sale.order & purchase.order) y sus lineas.
        Automaticamente computa el ratio de conversion para su posterior uso en implementaciones de flujos de compra/venta.
        TODO: Incluir historial de cambios, validaciones de documentos con locked_currency_id abiertos y otras validaciones.
    """,
    'version': '17.0.1.101',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['base', 'purhcase', 'sale'],
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
