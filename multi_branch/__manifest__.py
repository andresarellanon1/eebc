{
    'name': 'Multi empresas',
    'description': """
            Este modulo comprende las configuraciones para las multiples sucursales de la empresa.
    """,
    'version': '17.0.0.02',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
                'sale_management',
                'sale_stock', 'purchase_stock',
                'stock_account'
               ],
    'data': [
        "views/res_branch_views.xml",
        "security/ir.model.access.csv",
        "views/branch_res_users_views.xml",
        "views/branch_res_partner_views.xml",
        # "security/branch_security.xml",
        "views/branch_product_template.xml",
        "views/branch_purchase_order_views.xml",
        "views/branch_stock_picking_views.xml",
        "views/branch_stock_warehouse_views.xml",
        "views/branch_sale_order_views.xml",
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False
}
