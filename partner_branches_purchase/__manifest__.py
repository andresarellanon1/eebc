{
    'name': 'Costos de compras y valoración de inventario por sucursal',
    'summary': 'Implementa funcionalidad de proveedor principal y calcula últimos precios de proveedores a partir de documentos de compra.',
    'description': """
        Este módulo calcula el costo del inventario para las capas de inventario y para contabilidad
        utilizando el historial de proveedores de un artículo y la fecha de costos destino asociada a la línea de la orden de compra.
        Se ajusta al algoritmo FIFO o AVG para determinar el costo unitario (`standard_price`) de entrada que se aplicará a la capa generada.

        Además, se introduce un campo de costo contable para el producto (`accounting_standard_price`). Este costo se mantiene
        mediante un algoritmo configurable por categoría de producto, según las preferencias del usuario. A diferencia de `standard_price`,
        que se recalcula con cada compra para reflejar el costo específico de la capa generada, el campo `accounting_standard_price`
        se actualiza considerando no solo el costo de entrada del proveedor principal o el último proveedor, sino también
        el historial completo de capas de inventario.

        Este campo no se recalcula en función de las configuraciones de proveedores y está diseñado para reemplazar el uso
        de `standard_price` en los casos donde era importante que este último se mantuviera computado para todo el inventario.

        En este módulo, el campo `standard_price` se utiliza para calcular el costo unitario de la capa de valoración entrante y
        se actualiza específicamente en cada compra. Sin embargo, está vinculado a la relación del proveedor principal o último proveedor.
        Por lo tanto, no siempre refleja el precio más reciente de compra unitaria, sino el último precio del proveedor principal,
        dependiendo de si este comportamiento está activado mediante un campo booleano. Este funcionamiento es heredado del
        módulo `product_supplier_history`.
    """,
    'version': '17.0.2.12',
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
