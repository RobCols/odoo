from odoo import api, fields, models
import requests


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

        records = self.search([("product_id.is_empty", "=", "False"), ("product_uom_qty", ">", 0)])
        headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
        data = []
        for rec in records:
            for ol in rec.order_line:
                if ol.product_uom_qty < 1:
                    continue
                data.append(
                    {
                        "partnerId": ol.id,
                        "customerPartnerId": rec.partner_id.id,
                        "productPartnerId": ol.product_id.id,
                        "quantity": ol.product_uom_qty,
                        "forecastedOrder": False,
                        "accepted": True,
                        "cancelled": False,
                        "deliveryDate": rec.date_order.isoformat(),
                    }
                )
        r = requests.post(
            "https://api.litefleet.io/api/Orders/multiple", json=data, headers=headers
        )
        print(r.status_code)

        return True
