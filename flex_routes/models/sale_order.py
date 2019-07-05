from odoo import api, fields, models
from odoo.tools import safe_eval


class SaleOrder(models.Model):
    _inherit = "sale.order"

    route_id = fields.Many2one("route.route")
    route_sequence = fields.Integer()
    optimization_id = fields.Many2one("route.optimization")

    delivery_address_string = fields.Char(compute="_compute_delivery_address_string")

    google_shipping_url = fields.Char(compute="_compute_google_shipping_url")
    shipping_street_image = fields.Binary(related="partner_shipping_id.street_image")
    shipping_satellite_image = fields.Binary(
        related="partner_shipping_id.satellite_image"
    )
    non_empty_order_line = fields.One2many(
        "sale.order.line", compute="_compute_non_empty_order_line"
    )

    empty_order_line = fields.One2many(
        "sale.order.line", compute="_compute_non_empty_order_line"
    )
    delivery_state = fields.Selection(
        [("undelivered", "Nog niet afgeleverd"), ("delivered", "Afgeleverd")],
        default="undelivered",
    )

    @api.multi
    def set_delivery_state_to_delivered(self):
        self.ensure_one()
        self.delivery_state = "delivered"

    @api.multi
    def scan_pickups(self):
        self.ensure_one()
        action = self.env.ref(
            "product_empties_mobile.action_open_sale_order_mobile_view"
        ).read()
        if action:
            action = action[0]
        context = safe_eval(action.get("context", {}))
        context["so_id"] = self.id
        context["active_id"] = self.env.context["active_id"]
        context["active_ids"] = self.env.context["active_ids"]
        context["active_model"] = "sale.order"
        context["previous_action"] = self.env.ref(
            "flex_routes.flex_routes_sale_view_form"
        ).id
        context["ids"] = (
            self.env["sale.order"]
            .search([("route_id", "=", self.env.context["active_id"])])
            .ids
        )
        action["context"] = context

        return action

    @api.depends("order_line")
    def _compute_non_empty_order_line(self):
        for record in self:
            record.non_empty_order_line = record.order_line.filtered(
                lambda o: o.product_id.product_tmpl_id
                and not o.product_id.product_tmpl_id.is_empty
            )
            record.empty_order_line = record.order_line.filtered(
                lambda o: o.product_id.product_tmpl_id
                and o.product_id.product_tmpl_id.is_empty
            )

    @api.depends(
        "partner_shipping_id",
        "partner_shipping_id.partner_latitude",
        "partner_shipping_id.partner_longitude",
    )
    def _compute_google_shipping_url(self):
        for record in self:
            if record.partner_shipping_id:
                if (
                    not record.partner_shipping_id.partner_latitude
                    or not record.partner_shipping_id.partner_longitude
                ):
                    record.partner_shipping_id.geocode_one_partner_movetex()
                record.google_shipping_url = f"https://www.google.com/maps/dir/?api=1&destination={record.partner_shipping_id.partner_latitude},{record.partner_shipping_id.partner_longitude}"

    @api.depends(
        "partner_id",
        "partner_shipping_id",
        "partner_shipping_id.street_name",
        "partner_shipping_id.street_number",
        "partner_shipping_id.city_id",
        "partner_shipping_id.city",
        "partner_shipping_id.zip",
        "partner_shipping_id.street2",
    )
    def _compute_delivery_address_string(self):
        for record in self:
            address_string = ""
            if record.partner_id:
                address_string += record.partner_id.display_name
                if record.partner_shipping_id.street_name:
                    address_string += ", " + record.partner_shipping_id.street_name
                    if record.partner_shipping_id.street_number:
                        address_string += (
                            ", " + record.partner_shipping_id.street_number
                        )
                    if record.partner_shipping_id.city_id:
                        address_string += ", " + record.partner_shipping_id.city_id
                    elif record.partner_shipping_id.city:
                        if record.partner_shipping_id.zip:
                            address_string += f", {record.partner_shipping_id.zip} {record.partner_shipping_id.city}"
                        else:
                            address_string += f", {record.partner_shipping_id.city}"
                    if record.partner_shipping_id.street2:
                        address_string += f" ({record.partner_shipping_id.street2})"
            record.delivery_address_string = address_string

    @api.model
    def get_movetex_data(self):
        self.ensure_one()
        if (
            not self.partner_shipping_id.partner_longitude
            or not self.partner_shipping_id.partner_latitude
        ):
            self.partner_shipping_id.geocode_one_partner_movetex()
        payload = {
            "id": self.id,
            "destination": {
                "id": self.partner_shipping_id.id,
                "lon": self.partner_shipping_id.partner_longitude,
                "lat": self.partner_shipping_id.partner_latitude,
            },
            "deliveryWindow": {
                "startInSeconds": 10000,  # TODO
                "stopInSeconds": 12000,  # TODO
            },
            "depotId": 1,
            "preferredTransportationMode": "Car",  # TODO
            "allowedTransportationModes": "Car",  # TODO
            "revenue": 15,  # TODO
            "priority": 10,  # TODO
            "duedate": self.date_order.isoformat(),
            "name": self.name,
            "dropSize": [1],
            "extraDropDuration": 60,  # TODO
            "fixedDropDurationInSeconds": 5,  # TODO
            "variableDropDurationInSeconds": 10,  # TODO
            "extraDropDurationInSeconds": 0,  # TODO
        }
        return payload
