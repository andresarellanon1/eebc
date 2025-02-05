{
    "name": "Accounting Sale Origins",
    'summary': 'Vincula órdenes de venta y albaranes como documentos de origen en facturas.',
    'description': """
        Extiende las facturas en Odoo para incluir campos relacionados que permiten vincular órdenes de 
        venta y albaranes como documentos de origen. Facilita el rastreo y la gestión de las facturas en 
        relación con las ventas y entregas, mejorando la trazabilidad entre los procesos de ventas, 
        inventario y contabilidad.
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
