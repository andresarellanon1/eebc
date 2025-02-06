{
    'name': "EBBC NOTICES",
    'version': '17.0.1.108',
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    "summary": "Gestión de productos con aviso especial.",
    'description': """
        Módulo de gestión de productos con seguimiento especial para inventarios y compras. Permite controlar los movimientos de productos relacionados con un aviso de prueba, asegurando trazabilidad 
        precisa mediante la integración con registros de inventario y avisos asociados. Gestiona la creación de lotes, números de serie y validación de existencias, mejorando la visibilidad y 
        eficiencia en los movimientos de productos.
    """,
    'depends': ['purchase', 'account', 'base', 'sale_stock', 'stock'],

    "data": [
        "security/ir.model.access.csv",
        "views/notices_views.xml",
        "views/stock_move_views.xml",
        "views/menu.xml",
        "views/stock_picking_views.xml",
        "wizard/notice_file_wizard_view.xml",
        "wizard/select_notice_wizard_view.xml",
        "wizard/wizard_selection_line_view.xml",
        "wizard/wizard_selection_lot_line_view.xml",
        "wizard/split_stock_move_wizard_view.xml",








    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'eebc_notices/static/src/components/tab_change_handler.js',
    #     ],
    # },
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
