from odoo import api, fields, models
import requests
import json
import datetime


def get_auth_headers(env):
    ICPSudo = env["ir.config_parameter"].sudo()
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

    return {"Authorization": f"Bearer {r.json()['access_token']}"}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    forecasted = fields.Boolean("Forecasted Line", help="", default=False)
    accepted = fields.Boolean("Accepted", default=False)
    cancelled = fields.Boolean("Cancelled", default=False)
    proposed_forecast_date = fields.Datetime("Proposed Forecast Date", help="")
    delivery_date = fields.Datetime("Delivery Date", help="")
    forecast_id = fields.Char("Forecast ID")

    @api.model
    def sync_orders(self):
        records = self.search([("sync_needed", "=", True)])
        records.send_orders_to_forecasting_api()

    @api.multi
    def send_orders_to_forecasting_api(self):
        headers = get_auth_headers(self.env)
        data = []
        records = self.search(
            [("name", "not ilike", "total"), ("product_uom_qty", ">", 0)]
        )

        for ol in records.filtered(
            lambda ol: not ol.product_id.product_tmpl_id.is_empty
        ):
            data.append(
                {
                    "partnerId": ol.id,
                    "customerPartnerId": ol.order_id.partner_id.id,
                    "productPartnerId": ol.product_id.id,
                    "quantity": ol.product_uom_qty,
                    "forecastedOrder": False,
                    "accepted": ol.order_id.state in ["done", "sale"],
                    "cancelled": ol.order_id.state == "cancel",
                    "deliveryDate": ol.order_id.date_order.isoformat(),
                }
            )
        r = requests.put(
            "https://api.litefleet.io/api/Orders/multiple", json=data, headers=headers
        )
        print(r.status_code)

        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.order_id.forecast_line_ids.filtered(
            lambda i: i.product_id.id == res.product_id.id and not i.product_id.is_empty
        ):
            self.env["forecast.order.line"].create(
                {
                    "product_id": res.product_id.id,
                    "order_id": res.order_id.id,
                    "quantity": 0,
                    "proposed_forecast_date": False,
                    "forecast_id": 0,
                }
            )
        return res

    @api.multi
    def cancel_forecast(self):
        headers = get_auth_headers(self.env)

    @api.model
    def predict_purchases(self):
        headers = get_auth_headers(self.env)
        ICPSudo = self.env["ir.config_parameter"].sudo()

        orders_used = ICPSudo.get_param(
            "flex_forecasting.number_of_orders_used_in_forecast"
        )
        missed_expected_orders = ICPSudo.get_param(
            "flex_forecasting.max_number_of_missed_expected_orders"
        )
        weeks_without_orders = ICPSudo.get_param(
            "flex_forecasting.max_number_of_weeks_without_orders"
        )

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
                data["nbOfOrdersUsedInForecast"] = int(orders_used)
                data["maxNbOfMissedExpectedOrders"] = int(missed_expected_orders)
                data["maxNbOfWeeksWithoutOrders"] = int(weeks_without_orders)
                resp = requests.post(
                    "https://api.litefleet.io/api/Forecasts", json=data, headers=headers
                )
                if resp.status_code == 200:
                    response = resp.json()
                    sent_ids.append(
                        [record.product_id.id, record.order_id.partner_id.id]
                    )
                    if response.get("order", False) and response["order"].get(
                        "proposedForecastDate", False
                    ):
                        date = datetime.datetime.strptime(
                            response["order"]["proposedForecastDate"],
                            "%Y-%m-%dT%H:%M:%S",
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
                                "state": "draft",
                            }
                            order = SaleOrder.create(vals)
                        vals = {
                            "product_id": record.product_id.id,
                            "order_id": order.id,
                            "quantity": response["order"]["quantity"],
                            "proposed_forecast_date": date,
                            "forecast_id": response["order"]["partnerId"],
                        }
                        ForecastedOrderLine.create(vals)

                        vals = {
                            "product_id": record.product_id.id,
                            "order_id": order.id,
                            "product_uom_qty": response["order"]["quantity"],
                            "proposed_forecast_date": date,
                        }
                        OrderLine.create(vals)


class ForecastedOrderLine(models.Model):
    _name = "forecast.order.line"

    order_id = fields.Many2one("sale.order", "Order")
    product_id = fields.Many2one("product.product", "Product")
    quantity = fields.Integer("Hoeveelheid")
    accepted = fields.Boolean("Accepted", default=False)
    cancelled = fields.Boolean("Cancelled", default=False)
    proposed_forecast_date = fields.Datetime("Proposed Forecast Date", help="")
    forecast_id = fields.Char("Forecast ID")

    @api.multi
    def send_orders_to_forecasting_api(self):
        headers = get_auth_headers(self.env)
        data = []
        for record in self:
            data.append(
                {
                    "partnerId": record.forecast_id,
                    "customerPartnerId": str(record.order_id.partner_id.id),
                    "productPartnerId": str(record.product_id.id),
                    "quantity": record.quantity,
                    "accepted": record.accepted,
                    "cancelled": record.cancelled,
                    "forecastedOrder": False,
                    "proposedForecastDate": record.proposed_forecast_date.isoformat(),
                    "deliveryDate": record.order_id.date_order.isoformat(),
                }
            )
        if data:
            r = requests.put(
                "https://api.litefleet.io/api/Orders/multiple",
                json=data,
                headers=headers,
            )
            print(r.status_code)

        return True


class SaleOrder(models.Model):
    _inherit = "sale.order"

    forecast_line_ids = fields.One2many("forecast.order.line", "order_id")
    modification_deadline = fields.Datetime()
    synced = fields.Boolean("Synchronised with Movetex", default=False)

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

    @api.multi
    def write(self, vals):
        if "state" in vals:
            vals["synced"] = False

        return super().write(vals)

    @api.model
    def send_forecast_feedback(self):
        recs = self.search([("synced", "=", False)])
        matched_forecast_ids = []
        unmatched_lines = []
        for record in recs:
            unmatched_lines.append(record.order_line)
            for line in record.order_line:
                for forecasted_line in record.forecast_line_ids:
                    if forecasted_line.product_id != line.product_id:
                        continue
                    forecasted_line.accepted = record.state in ["done", "sale"]
                    forecasted_line.quantity = line.product_uom_qty
                    matched_forecast_ids.append(forecasted_line.id)
                    unmatched_lines.remove(line)
            for forecasted_line in record.forecast_line_ids.filtered(
                lambda i: i.id not in matched_forecast_ids
            ):
                forecasted_line.cancelled = True
            if unmatched_lines:
                unmatched_lines.send_orders_to_forecasting_api()
            record.synced = True
        recs.forecast_line_ids.send_orders_to_forecasting_api()
