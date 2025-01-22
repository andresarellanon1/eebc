{
    'name': 'Historial de proveedores',
    'summary': 'Implementa funcionalidad de proveedor principal y calcula ultimos precios de proveedores apartir de documentos de compra.',
    'description': """
            Este módulo muestra campos extra para configuración de proveedores en el inventario.
            Agrega funcionalidad para calcular los últimos precios de compra cuando se agregan líneas de orden de compra para un producto.
            Agrega un historial de compras (modelo nuevo) a la vista detallada del product.template.
    """,
    'version': '17.0.1.001',
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
        'purchase_landing_lines',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_supplierinfo.xml',
        'views/product_supplierinfo_history.xml',
        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
