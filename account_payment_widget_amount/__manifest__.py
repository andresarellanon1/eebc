{
    "name": "Account Payment Widget Amount",
    "summary": "Extends the payment widget to be able to choose the payment",
    "version": "17.0.0.0.1",
    "category": "Account-payment",
    "author": "Quadro Soluciones",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "account_payment_widget_amount/static/src/xml/account_payment.xml",
            "account_payment_widget_amount/static/src/js/account_payment_field.esm.js",
        ],
    },
}
