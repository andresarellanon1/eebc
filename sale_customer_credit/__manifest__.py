{
    "name": "Customer Sales Credit",
    "summary": "Gestión y validación de crédito de clientes.","
    "description": """
            Este módulo se centra en la gestión del crédito de los clientes dentro de Odoo. Permite verificar y controlar el crédito de los partners, 
            bloquear ventas si se excede el límite de crédito, y ofrecer una opción de "Llave de crédito" para excepciones. Integra estas funcionalidades 
            con el sistema de ventas y configuraciones personalizadas para asegurar que las operaciones comerciales no sobrepasen los límites de crédito 
            establecidos.
    """,
    "version": "17.0.3.005",
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
    "data": [
        "views/res_partner.xml",
        "views/res_config_settings.xml",
    ],
    "license": "LGPL-3",
}
