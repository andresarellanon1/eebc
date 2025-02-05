{
    'name': 'Costos de compras y valoración de inventario por sucursal',
    'summary': 'Implementa funcionalidad de proveedor principal y calcula últimos precios de proveedores a partir de documentos de compra.',
    'description': """
        Este módulo calcula el costo de inventario y contable usando el historial de proveedores y las 
        órdenes de compra. Introduce el campo accounting_standard_price, que se actualiza con un algoritmo 
        configurable y reemplaza el standard_price para mantener un costo constante. El standard_price se 
        recalcula en cada compra y refleja el costo del proveedor principal o último proveedor, dependiendo 
        de la configuración.
    """,
    'version': '17.0.1.002',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'purchase',
        'purchase_stock',
        'approvals_purchase',
        'purchase_requisition_stock',
        'stock_accountant',
        'stock',
        'stock_account',
        'product',
        'contacts',
        'account',
        'account_accountant',
    ],
    'data': [
    ],
    "license": "LGPL-3",
    'installable': True
}
