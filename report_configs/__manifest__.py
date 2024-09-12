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
        'views/account_invoice_views.xml',
        'templates/out_invoice_template_custom.xml',
        'templates/external_layout_invoice_custom.xml',
        'templates/report_invoice_inherit_custom.xml',
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
