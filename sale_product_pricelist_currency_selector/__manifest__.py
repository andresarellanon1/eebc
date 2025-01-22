{
    'name': 'Lista de precios por linea de venta en Divisa Objetivo',
    'summary': 'Este modulo implementa metodos para computar la lista de precios y el precio unitario tomando en cuenta la divisa secundaria para la empresa.',
    'description': """
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
    'version': '17.0.2.005',
    'website': 'https://quadrosoluciones.com',
    'author': 'Quadro Soluciones',
    'depends': ['sale', 'currency_lock', 'sale_product_pricelist'],
    'data': [
        'views/res_config_settings.xml',
    ],
    "license": "LGPL-3",
    'installable': True
}
