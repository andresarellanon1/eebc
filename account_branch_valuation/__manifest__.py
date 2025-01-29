{
    "name": "Accounting branch Valuation",
    'summary': 'Valoración de Inventarios Personalizada y Gastos Contables.',
    "description": """
        Este módulo extiende la funcionalidad estándar de Odoo para proporcionar una valoración de inventarios
        y gastos contables personalizados. Incluye características avanzadas para la valoración de capas de 
        inventario y ventas, permitiendo la incorporación de efectos fiscales en los cálculos contables. 
        El módulo utiliza campos y cálculos personalizados para garantizar que los informes financieros y las 
        transacciones contables reflejen con precisión los costos y los impactos fiscales asociados con las 
        ventas y el inventario.
    """,
    "version": "17.0.1.001",
    "depends": [
        "base",
        "sale",
        "account",
        "account_accountant",
        "account_sale_origins",
        "account_purchase_origins",
        "sale_branch_valuation",
        "purchase_branch_valuation"
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "data": [
        "views/account_move.xml",
    ],
    "license": "LGPL-3",
}
