{
    "name": "Partner Branches",
    'summary': 'Permite gestionar contactos como sucursales, facilitando la organización y el manejo de información de sucursales bajo una entidad principal.',
    'description': """
        Extiende la funcionalidad de los contactos en Odoo para permitir la gestión de sucursales, incluyendo 
        la asignación de nombres, números y relaciones jerárquicas. Facilita la organización de contactos que 
        representan sucursales de una entidad principal.
    """,
    "version": "17.0.3.001",
    "depends": [
        "stock",
        "partner_customer",
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "data": [
        "views/res_partner.xml"
    ],
    "license": "LGPL-3",
}
