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
        'views/account_invoice_views.xml',
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
