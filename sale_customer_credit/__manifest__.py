{
    "name": "Customer Sales Credit",
    "version": "17.0.3.004",
    "depends": [
        "base",
        "sale",
        "sale_account_accountant",
        "contacts",
        "contacts_enterprise",
        "account_accountant",
        "base_address_extended",
        "partner_customer",
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "description": """
            Campos para clientes. Se agregan campos y validaciones de credito a flujos de venta.
    """,
    "data": [
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "license": "LGPL-3",
}
