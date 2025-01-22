{
    "name": "Product Line Configs",
    "version": "17.0.1.001",
    "depends": ['account', 'sale'],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
        Este módulo conforma las configuraciones para las lineas de productos de forma global.
    """,
    "data": [
        "views/inherit_sale_order_form_view.xml",
        "views/inherit_account_move_form_view.xml",
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
