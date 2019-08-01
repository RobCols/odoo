from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import requests
import json
import sys
import time


class RouteOptimization(models.Model):
    _name = "route.optimization"
    _description = "Routeoptimalisaties"
    _rec_name = "date"

    date = fields.Date("Datum")
    optimization_preparation_ids = fields.One2many(
        "route.optimization.preparation", "optimization_id"
    )
    sale_order_ids = fields.One2many("sale.order", "optimization_id")
    route_ids = fields.One2many("route.route", "optimization_id")
    last_batch_job = fields.Integer()

    @api.multi
    @api.depends("route_ids")
    def cancel_optimization(self):
        """
        UNDO THE MOVETEX MAGIC
        """

        self.ensure_one()
        self.route_ids.unlink()

    @api.multi
    @api.depends("sale_order_ids", "date")
    def start_optimization(self):
        """
        DO THE MOVETEX MAGIC
        """
        self.ensure_one()

        test = datetime.combine(self.date, datetime.min.time())

        search_domain = [
            "&",
            ("date_order", ">=", datetime.combine(self.date, datetime.min.time())),
            ("date_order", "<=", datetime.combine(self.date, datetime.max.time())),
        ]

        orders = self.env["sale.order"].search(search_domain)

        if not orders:
            raise UserError(_("No orders were found for the specified date"))

        self.sale_order_ids = orders

        if not self.optimization_preparation_ids:
            raise UserError(_("No preparations were found"))

        token = self.get_token()

        payload = {
            "deliveries": [order.get_movetex_data() for order in self.sale_order_ids],
            "vehicles": [
                opt.get_movetex_data() for opt in self.optimization_preparation_ids
            ],
            "vehicleTypes": [
                {
                    "vehicleTypeId": 1,
                    "transportationMode": "Car",
                    "travelMode": "driving",
                    "absRangeInDropSize": [20],
                }
            ],
            "distanceComputationMethod": "OpenStreetMap",
        }

        payload.update({"depots": self.get_depots_from_vehicle(payload)})
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(
            "https://api.litefleet.io/api/CVRPTW/calculate/",
            json=payload,
            headers=headers,
        )
        self.last_batch_job = r.json().get("batchJobId", False)
        if not self.last_batch_job:
            raise UserError(
                _(
                    f"Movetex Batch Job Error: \n"
                    + json.dumps(r.json(), indent=2)
                    + "\n\nRequest data:\n"
                    + json.dumps(payload, indent=2)
                )
            )
        r = requests.get(
            "https://api.litefleet.io/api/CVRPTW/result/"
            + str(self.last_batch_job)
            + "/",
            headers=headers,
        )

        while r.status_code != 200:
            r = requests.get(
                "https://api.litefleet.io/api/CVRPTW/result/"
                + str(self.last_batch_job)
                + "/",
                headers=headers,
            )
            time.sleep(3)
        response = r.json()
        if response.get("routes", False):
            RouteModel = self.env["route.route"]
            for route in response.get("routes"):
                if not route.get("deliveryTasks", False):
                    continue
                user_id = int(route["vehicleId"].split("_")[1])
                vehicle_id = int(route["vehicleId"].split("_")[0])
                created_route = RouteModel.create(
                    {"user_id": user_id, "date": self.date, "vehicle_id": vehicle_id}
                )
                for delivery in route["deliveryTasks"]:
                    order = self.env["sale.order"].browse(int(delivery["deliveryId"]))
                    order.route_id = created_route.id
                    order.route_sequence = delivery["indexInRoute"]
                self.route_ids |= created_route
            for route in self.route_ids:
                route.generate_route_picking_ids()

    @api.model
    def get_depots_from_vehicle(self, payload):
        vehicles = payload["vehicles"]
        depots = []
        if not vehicles:
            return
        for v in vehicles:
            if any(d["id"] == v["depotId"] for d in depots):
                continue
            lat = self.env["res.partner"].browse(int(v["depotId"])).partner_latitude
            lng = self.env["res.partner"].browse(int(v["depotId"])).partner_longitude
            if not lat or not lng:
                self.env["res.partner"].browse(
                    int(v["depotId"])
                ).geocode_one_partner_movetex()
            depots.append(
                {
                    "id": v["depotId"],
                    "location": {
                        "id": v["depotId"],
                        "lat": self.env["res.partner"]
                        .browse(int(v["depotId"]))
                        .partner_latitude,
                        "lon": self.env["res.partner"]
                        .browse(int(v["depotId"]))
                        .partner_longitude,
                    },
                }
            )
        return depots

    @api.model
    def get_token(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        client_id = ICPSudo.get_param("flex_forecasting.client_id")
        client_secret = ICPSudo.get_param("flex_forecasting.client_secret")
        username = ICPSudo.get_param("flex_forecasting.username")
        password = ICPSudo.get_param("flex_forecasting.password")

        payload = {
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        }

        r = requests.post("https://idp.litefleet.io/connect/token", data=payload)

        return r.json()["access_token"]
