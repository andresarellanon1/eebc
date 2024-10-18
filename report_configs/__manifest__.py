{
    'name': 'Reportes personalizados',
    'description': """
            Este modulo comprende las personalizaciones de los reportes de la compañia.
    """,
    'version': '17.0.0.01',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'account',
               ],
    'data': [
        'templates/out_invoice_template_custom.xml',
        'templates/out_material_template.xml',
        'templates/out_saleorder_template_custom.xml',
        'templates/out_purchaseorder_template_custom.xml',
        'templates/out_stock_picking_out_template.xml',
        'templates/external_layout_invoice_custom.xml',
        'templates/report_invoice_inherit_custom.xml',
        'templates/report_styles.xml',
        'views/account_invoice_views.xml',
        'views/account_material_views.xml',
        'views/account_stock_views.xml',
        'views/account_saleorder_views.xml',
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
