{
    'name': "Partner Customer Extension",
    'summary': 'Extiende la funcionalidad de contactos y órdenes de venta en Odoo.',
    'description': """
        Este módulo extiende la funcionalidad de los contactos y órdenes de venta en Odoo, agregando campos 
        adicionales para la clasificación de clientes y mejorando la gestión de información comercial. Facilita 
        la configuración de clientes y la automatización de procesos en las órdenes de venta.
    """,
    'version': '17.0.3.002',
    'depends': [
        "sale",
        "contacts"
    ],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    "data": [
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
