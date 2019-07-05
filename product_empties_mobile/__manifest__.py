{
    "name": "Product Empties Mobile",
    "version": "12.0.1.0.0",
    "author": "Abstractive BVBA",
    "website": "http://www.abstractive.be",
    "depends": ["sale", "product_empties"],
    "summary": "Sale Order mobile view",
    "data": [
        "view/assets.xml",
        "wizard/so_mobile_wizard_view.xml",
        "view/product_view.xml",
        "view/sale_order_view.xml",
    ],
    "qweb": ["static/src/xml/sale_order_mobile.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "",
}
