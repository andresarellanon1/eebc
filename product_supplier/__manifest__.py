{
    'name': "Proveedor de productos",
    'version': '17.0.1.05',
    'depends': ['stock', 'contacts', 'product', 'purchase'],
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo conforma las configuraciones de los proveedores de productos.

    """,
    "data": [
        "views/product_supplierinfo.xml",
        "views/inherit_purchase_order_form_view.xml"
    ],
    "application": False,
    "installable": True,
    "license": "LGPL-3",
}
