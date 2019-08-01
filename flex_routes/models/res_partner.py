from odoo import models, api, fields, exceptions, _
import datetime
import requests
import json


class ResPartner(models.Model):
    _inherit = "res.partner"

    routing_zoomlevel = fields.Integer()

    satellite_image = fields.Binary("Satellietbeeld")
    street_image = fields.Binary("Straatbeeld")
    is_depot = fields.Boolean("Is depot", default=False)
    has_delivery_address = fields.Boolean(compute="_compute_has_delivery_address")
    depot_id = fields.Many2one(
        "res.partner", string="Depot-adres", domain=[("is_depot", "=", True)]
    )

    @api.depends("child_ids")
    def _compute_has_delivery_address(self):
        for record in self:
            for partner in record.child_ids:
                if partner.type == "delivery":
                    record.has_delivery_address = True

    @api.multi
    def button_geocode_movetex(self):
        for record in self:
            record.geocode_one_partner_movetex()

    @api.multi
    def geocode_one_partner_movetex(self):
        self.ensure_one()
        token = self.env["route.optimization"].get_token()

        headers = {"Authorization": f"Bearer {token}"}

        geo_request = {
            "streetName": self.street_name,
            "houseNumber": self.street_number,
            "postalCode": self.zip or self.city_id.zipcode,
            "city": self.city,
            "country": self.country_id.name,
            "distanceComputationMethod": "Here",
        }

        r = requests.post(
            "https://api.litefleet.io/api/Geocode/", json=geo_request, headers=headers
        )
        results = r.json()["results"]

        if not results:
            raise exceptions.UserError(
                _(
                    f"Can't geocode address for {self.name or self.parent_id.name}:"
                    + json.dumps(r.json(), indent=2)
                )
            )

        for result in results:
            self.date_localization = datetime.date.today()
            self.partner_latitude = result["lat"]
            self.partner_longitude = result["lon"]
            break
