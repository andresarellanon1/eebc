{
    'name': 'Listas de precios en producto',
    'summary': 'Visor de lista de precios en productos y lineas de documentos de venta.',
    'description': """
        Este módulo muestra una tabla con la lista de precios dentro de la vista de cada producto.
        Muestra una widget de selección para la lista de precios en el documento de venta y el documento de factura de cliente.
        Actualiza el precio unitario de la línea en cuestión correspondiente con la lista de precios seleccionada en cualquiera de estos dos documentos.
        Este modulo implementa metodos para computar la lista de precios y el precio unitario tomando en cuenta la divisa secundaria para la empresa.
        Seleccion default:
            Al seleccionar el producto de la linea se implementa un algoritmo de prioridades.
            Las prioridades se definen por la lista de precio del cliente (base de odoo) y la lista prioritaria agregada en un modulo personalizado.
            El algoritmo encuentra la lista de precios con mayor prioridad en caso de que el producto se encuentre en mas de una.
        Multi divisa:
            Si la orden cambio de divisa, busca una lista de precio con el mismo nombre pero en la divisa objetivo.
        Multi sucursal:
            Encuentra solamente listas de precio correspondientes a la sucursal del vendedor de la orden.
    """,
    'version': '17.0.4.004',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': [
        'stock',
        'product',
        'sale_management',
        'product_email_template',
        'partner_priority_pricelist',
        'currency_lock'
        # todo: agregar moudlo de  contabilidad mexicana para depender del campod unspsc
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist.xml',
        'views/product_pricelist_line.xml',
        'views/product_template.xml',
        'views/sale_order_line.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
