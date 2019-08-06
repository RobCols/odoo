from odoo import http
import json


class MapController(http.Controller):
    @http.route("/route/map", auth="public")
    def index(self, **kw):
        Route = (
            http.request.env["route.route"]
            .sudo()
            .search([("id", "=", kw["active_id"])])
        )
        result = {}
        result["depot"] = {
            "latitude": Route.depot_latitude,
            "longitude": Route.depot_longitude,
        }
        result["sale_order_coords"] = []
        for order_id in Route.sale_order_ids.sorted(key=lambda o: o.route_sequence):
            result["sale_order_coords"].append(
                {
                    "name": order_id.partner_id.name,
                    "address": order_id.partner_shipping_id.street
                    + "\n"
                    + (
                        order_id.partner_shipping_id.city
                        or order_id.partner_shipping_id.city_id.name
                    ),
                    "sequence": order_id.route_sequence,
                    "latitude": order_id.partner_latitude,
                    "longitude": order_id.partner_longitude,
                }
            )

        return http.request.render(
            "flex_courier_rounds.map_with_markers", {"route": json.dumps(result)}
        )
