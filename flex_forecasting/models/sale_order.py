from odoo import api, fields, models
import requests


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def send_orders_to_forecasting_api(self):
        # records = self.search([("sync_needed", "=", True)])
        records = self.search([])
        headers = {
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkRCMDMxOTBFOEY3RDZDRjdBNDgyQUM5NEREQ0VEM0M4OUEzMDJGRjIiLCJ0eXAiOiJKV1QiLCJ4NXQiOiIyd01aRG85OWJQZWtncXlVM2M3VHlKb3dMX0kifQ.eyJuYmYiOjE1NTU1NzgyNzgsImV4cCI6MTU1NTU4MTg3OCwiaXNzIjoiaHR0cHM6Ly9pZHAubGl0ZWZsZWV0LmlvIiwiYXVkIjpbImh0dHBzOi8vaWRwLmxpdGVmbGVldC5pby9yZXNvdXJjZXMiLCJNb3ZldGVYTGl0ZUZsZWV0QXBpIl0sImNsaWVudF9pZCI6IlB1YmxpY0xpdGVGbGVldEFwaS0xIiwic3ViIjoiOSIsImF1dGhfdGltZSI6MTU1NTU3ODI3OCwiaWRwIjoibG9jYWwiLCJuYW1lIjoiOSIsInNjb3BlIjpbIk1vdmV0ZVhMaXRlRmxlZXRBcGkiXSwiYW1yIjpbInB3ZCJdfQ.oQrLGadae3mMk2Nd5Z6IU2xwiiwVV21IMu-Vgq-XuTk9F0lyXqL3jKg-lBY_yd0WohESvlUpkFDEByhvIIyt4yGoDcMUN65IAVxGPXwG4JrkhTnmEvN0mgIjLvpZh-YshoJ4zr4pSB9PjBscWZURg7vk5iMnmPD_s5XACtMAqIUFR5nG0pkhTsWbvFIULtFA3pZvezlt-c5P8YAaf2eV3qg9unS9hNXHHsqchJj-cN7lgK55-DFYjPBldwboFFsfG9dLptSWvDCB0u6w8bj-8_-DntNz1jKzhfaWolBfa3szAOBXoBJLU1TU6FflY9g5qZCbgnmTjervmaQ-2DVmQw"
        }
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
