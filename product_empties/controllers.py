from odoo import http
from odoo.addons.base_rest.controllers import main
from odoo.http import Controller, ControllerType, Response, request, route


class EmptiesApi(main.RestController):
    _root_path = "/api/products/"
    _collection_name = "product_empties.services"
    _default_auth = "public"
