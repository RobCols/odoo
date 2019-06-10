# -*- coding: utf-8 -*-
from odoo import http

# class FlexForecasting(http.Controller):
#     @http.route('/flex_forecasting/flex_forecasting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flex_forecasting/flex_forecasting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('flex_forecasting.listing', {
#             'root': '/flex_forecasting/flex_forecasting',
#             'objects': http.request.env['flex_forecasting.flex_forecasting'].search([]),
#         })

#     @http.route('/flex_forecasting/flex_forecasting/objects/<model("flex_forecasting.flex_forecasting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flex_forecasting.object', {
#             'object': obj
#         })
