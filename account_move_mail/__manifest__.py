{
    "name": "Mail composer",
    "version": "17.0.0.10",
    "depends": ['account','mail','sale'],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
        Este módulo conforma las configuraciones para la composicion de los correos.
    """,
    "data": [
        "views/_inherit_move_send_form.xml",
        "views/_inherit_sale_move_send_form.xml"
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}