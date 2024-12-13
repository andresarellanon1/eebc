{
    'name': "EBBC NOTICES",
    'version': '17.0.1.97',
    'author': "Quadro Soluciones",
    'website': 'https://quadrosoluciones.com/',
    'category': 'other',
    'description': """
        Este modulo es para los avisos.

    """,
    'depends': ['purchase', 'account','base','sale_stock','stock'],
 
    "data": [
        "security/ir.model.access.csv",
        "views/notices_views.xml",
        "views/menu.xml",
        "views/stock_picking_views.xml",
        "wizard/notice_file_wizard_view.xml",
        "wizard/select_notice_wizard_view.xml",
        "wizard/wizard_selection_line_view.xml",



        
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

