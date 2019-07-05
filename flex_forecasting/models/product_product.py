from odoo import api, fields, models
import requests
import datetime


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_forecast_sync = fields.Date(string="Last sync to forecast API")
    sync_needed = fields.Boolean(compute="_compute_sync_needed", default=True)

    @api.depends("last_forecast_sync", "write_date")
    def _compute_sync_needed(self):
        for record in self:
            if not record.last_forecast_sync:
                record.sync_needed = True
            record.sync_needed = record.last_forecast_sync <= record.write_date

    @api.model
    def send_products_to_forecasting_api(self):
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

        records = self.search(["|", ("active", "=", True), ("active", "=", False)])

        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

        data = []
        date = datetime.datetime(1970, 1, 1)
        for rec in records:
            data.append(
                {
                    "partnerId": rec.id,
                    "name": rec.name,
                    "active": rec.active,
                    "startDate": date.isoformat(),
                }
            )

        r = requests.post(
            "https://api.litefleet.io/api/Products/multiple", json=data, headers=headers
        )

        return r.status_code
