# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.base_rest.controllers import main
from odoo.http import Controller, ControllerType, Response, request, route


class MobileApi(main.RestController):
    _root_path = "/api/"
    _collection_name = "user_settings.services"
    _default_auth = "user"


class PublicApi(main.RestController):
    _root_path = "/api/public/"
    _collection_name = "signup.services"
    _default_auth = "public"
