from odoo import api, fields, models
import requests
import json
import datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    forecasted = fields.Boolean("Forecasted Line", help="", default=False)
    accepted = fields.Boolean("Accepted", default=False)
    cancelled = fields.Boolean("Cancelled", default=False)
    proposed_forecast_date = fields.Datetime("Proposed Forecast Date", help="")
    delivery_date = fields.Datetime("Delivery Date", help="")
    forecast_id = fields.Char("Forecast ID")

    @api.model
    def send_orders_to_forecasting_api(self):
        # records = self.search([("sync_needed", "=", True)])
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

        records = self.search(
            [("name", "not ilike", "total"), ("product_uom_qty", ">", 0)]
        )
        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
        data = []
        for ol in records.filtered(
            lambda ol: not ol.product_id.product_tmpl_id.is_empty
            and ol.order_id.state in ["draft", "sent", "done", "sale"]
        ):
            data.append(
                {
                    "partnerId": ol.id,
                    "customerPartnerId": ol.order_id.partner_id.id,
                    "productPartnerId": ol.product_id.id,
                    "quantity": ol.product_uom_qty,
                    "forecastedOrder": False,
                    "accepted": True,
                    "cancelled": False,
                    "deliveryDate": ol.order_id.date_order.isoformat(),
                }
            )
        r = requests.post(
            "https://api.litefleet.io/api/Orders/multiple", json=data, headers=headers
        )
        print(r.status_code)

        return True

    @api.model
    def predict_purchases(self):
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

        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

        records = self.search(
            [("name", "not ilike", "total"), ("product_uom_qty", ">", 0)]
        )
        sent_ids = []
        SaleOrder = self.env["sale.order"]
        OrderLine = self
        ForecastedOrderLine = self.env["forecast.order.line"]
        for record in records.filtered(
            lambda ol: not ol.product_id.product_tmpl_id.is_empty
            and ol.order_id.state in ["draft", "sent", "done", "sale"]
        ):
            if [record.product_id.id, record.order_id.partner_id.id] not in sent_ids:
                data = {}
                data["productPartnerId"] = record.product_id.id
                data["customerPartnerId"] = record.order_id.partner_id.id
                data["nbOfOrdersUsedInForecast"] = 2
                data["maxNbOfMissedExpectedOrders"] = 2
                data["maxNbOfWeeksWithoutOrders"] = 4
                resp = requests.post(
                    "https://api.litefleet.io/api/Forecasts", json=data, headers=headers
                )
                response = resp.json()
                print(response)
                sent_ids.append([record.product_id.id, record.order_id.partner_id.id])
                if response.get("order", False) and response["order"].get(
                    "proposedForecastDate", False
                ):
                    date = datetime.datetime.strptime(
                        response["order"]["proposedForecastDate"], "%Y-%m-%dT%H:%M:%S"
                    )
                    order = SaleOrder.search(
                        [
                            "&",
                            ("partner_id", "=", record.order_id.partner_id.id),
                            ("date_order", "=", date),
                        ]
                    )
                    if not order:
                        vals = {
                            "date_order": date,
                            "partner_id": record.order_id.partner_id.id,
                            "state": "sent",
                        }
                        order = SaleOrder.create(vals)
                    print(order)
                    vals = {
                        "product_id": record.product_id.id,
                        "order_id": order.id,
                        "product_uom_qty": response["order"]["quantity"],
                        "proposed_forecast_date": date,
                    }
                    line = OrderLine.create(vals)
                    print(line)
                    vals = {
                        "product_id": record.product_id.id,
                        "order_id": order.id,
                        "quantity": response["order"]["quantity"],
                        "proposed_forecast_date": date,
                        "forecast_id": response["order"]["partnerId"],
                    }
                    ForecastedOrderLine.create(vals)


class ForecastedOrderLine(models.Model):
    _name = "forecast.order.line"

    order_id = fields.Many2one("sale.order", "Order")
    product_id = fields.Many2one("product.product", "Product")
    quantity = fields.Integer("Hoeveelheid")
    accepted = fields.Boolean("Accepted", default=False)
    cancelled = fields.Boolean("Cancelled", default=False)
    proposed_forecast_date = fields.Datetime("Proposed Forecast Date", help="")
    forecast_id = fields.Char("Forecast ID")

    @api.model
    def send_to_movetex(self):
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

        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
        data = []
        for record in self:
            data.append(
                {
                    "partnerId": record.forecast_id,
                    "customerPartnerId": record.order_id.partner_id,
                    "quantity": record.quantity,
                    "accepted": record.accepted,
                    "cancelled": record.cancelled,
                    "proposedForecastDate": record.proposed_forecast_date,
                    "deliveryDate": record.order_id.date_order,
                }
            )
        r = requests.put(
            "https://api.litefleet.io/api/Orders/multiple", json=data, headers=headers
        )
        print(r.status_code)

        return True


class SaleOrder(models.Model):
    _inherit = "sale.order"

    forecast_line_ids = fields.One2many("forecast.order.line", "order_id")
    modification_deadline = fields.Datetime()

    @api.model
    def create(self, vals):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        timedelta = int(ICPSudo.get_param("flex_forecasting.modification_deadline_hrs"))
        vals.update(
            {
                "modification_deadline": datetime.datetime.now()
                + datetime.timedelta(hours=timedelta)
            }
        )
        res = super().create(vals)
        return res
