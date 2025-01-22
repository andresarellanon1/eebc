{
    "name": "Customer Sales",
    "version": "17.0.1.001",
    "depends": [
        "base",
        "sale",
        "contacts",
        "contacts_enterprise",
        "account",
        "account_accountant",
        "base_address_extended",
        "weekdays"
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
            Campos para clientes. Agrega campos que se originan del sistema del cliente.
            Este modulo existe para albergar campos y datos de naturaleza ajena a odoo, originados de una "entrada" de datos del cliente.
    """,
    "data": [
        "views/sale_order.xml",
    ],
    "license": "LGPL-3",
}
