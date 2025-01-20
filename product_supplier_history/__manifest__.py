{
    'name': 'Historial de proveedores',
    'summary': 'Implementa funcionalidad de proveedor principal y calcula ultimos precios de proveedores apartir de documentos de compra.',
    'description': """
            Este módulo muestra campos extra para configuración de proveedores en el inventario.
            Agrega funcionalidad para calcular los últimos precios de compra cuando se agregan líneas de orden de compra para un producto.
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
        'partner_branches',
        'purchase_landing_lines',
        'purchase_supplier_history',
        'currency_lock'],
    'data': [
        # 'views/product_supplierinfo_views.xml',
        # 'views/product_supplierinfo_history_views.xml',
        # 'views/product_template_views.xml',
        # 'views/purchase_order_views.xml',
        # 'views/res_partner_views.xml',
        # 'security/ir.model.access.csv',
    ],
    "license": "LGPL-3",
    'installable': True
}
