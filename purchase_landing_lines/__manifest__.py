{
    "name": "Fecha costo destino en documento de compra",
    "summary": "",
    "description": """
            Este módulo muestra campos extra para los documentos de compra.
            Agrega funcionalidad para semi-automatizar la integración del flujo de costos destino desde los documentos de compra.
            La automatización solo funciona para un único registro de costos destino por documento de compra.
            Cuando un documento de compra tiene un "costo destino" asignado, al validar los traslados correspondientes a ese documento de compra,
            tanto las capas de valoración de inventario (stock.valuation.layer) como los movimientos (stock.move) generados con orígen en esa compra;
            usan la fecha del "costo destino" para hacer conversiones de divisa.
    """,
    "version": "17.0.1.22",
    "website": "https://quadrosoluciones.com",
    "author": "Quadro Soluciones",
    "depends": ["stock", "purchase_stock", "purchase", "stock_landed_costs", "l10n_mx_edi_landing"],
    "data": [
        "views/purchase_order_views.xml",
        "views/stock_landed_cost_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
