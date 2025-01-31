{
    "name": "Accounting Purchase Origins",
    "summary": "Vincula órdenes de compra como documentos de origen en facturas.",
    "description": """
        Este módulo extiende las facturas en Odoo, añadiendo un campo para vincular automáticamente las órdenes 
        de compra como documentos de origen. Facilita el seguimiento entre compras y facturación, y permite ajustes 
        manuales si es necesario.
    """,
    "version": "17.0.1.001",
    "depends": [
        "base",
        "sale",
        "account",
        "account_accountant"
    ],
    "author": "Quadro Soluciones",
    "website": "https://quadrosoluciones.com/",
    "category": "other",
    "data": [
    ],
    "license": "LGPL-3",
}
