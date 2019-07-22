{
    "name": "Flex-Delivery Routes",
    "version": "1",
    "summary": "Routeberekening voor Flex-Delivery",
    "category": "",
    "author": "Abstractive BVBA",
    "maintainer": "Abstractive BVBA",
    "website": "http://abstractive.be",
    "license": "OPL-1",
    "contributors": [""],
    "depends": [
        "base",
        "sale",
        "fleet",
        "base_geolocalize",
        "base_address_extended",
        "web_widget_url_advanced",
    ],
    "data": [
        "data/access_groups.xml",
        "data/hide_menus_for_carrier.xml",
        "views/route_view.xml",
        "views/route_optimization_view.xml",
        "views/fleet_vehicle.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "views/sale_order_tree.xml",
        "views/sale_order_form.xml",
        "views/product_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
