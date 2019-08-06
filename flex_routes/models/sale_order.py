from odoo import api, fields, models, _
from odoo.tools import safe_eval
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    courier_note = fields.Text("Note")
    route_id = fields.Many2one("route.route")
    route_sequence = fields.Integer()
    optimization_id = fields.Many2one("route.optimization")

    delivery_address_string = fields.Char(compute="_compute_delivery_address_string")
    depot_id = fields.Many2one("res.partner", related="partner_shipping_id.depot_id")
    google_shipping_url = fields.Char(compute="_compute_google_shipping_url")
    shipping_street_image = fields.Binary(related="partner_shipping_id.street_image")
    shipping_satellite_image = fields.Binary(
        related="partner_shipping_id.satellite_image"
    )
    non_empty_order_line = fields.One2many(
        "sale.order.line", compute="_compute_non_empty_order_line"
    )
    delivery_info = fields.Text(related="partner_shipping_id.comment")
    empty_order_line = fields.One2many(
        "sale.order.line", compute="_compute_non_empty_order_line"
    )
    delivery_state = fields.Selection(
        [("undelivered", "Nog niet afgeleverd"), ("delivered", "Afgeleverd")],
        compute="_compute_delivery_state",
    )

    total_crate_equivalence = fields.Float(compute="_compute_total_crate_equivalence")

    @api.depends("order_line")
    def _compute_total_crate_equivalence(self):
        for record in self:
            total_crate_equivalence = 0
            for line in record.order_line:
                total_crate_equivalence += (
                    line.product_uom_qty * line.product_id.crate_equivalence
                )
            record.total_crate_equivalence = total_crate_equivalence

    flex_color = fields.Integer(compute="_compute_flex_color")

    @api.depends("delivery_state")
    def _compute_flex_color(self):
        for record in self:
            if record.delivery_state == "undelivered":
                record.flex_color = 2
                continue
            record.flex_color = 10

    @api.multi
    def _compute_delivery_state(self):
        for record in self:
            if any(not i.delivery_state for i in record.non_empty_order_line):
                record.delivery_state = "undelivered"
            elif record.non_empty_order_line:
                record.delivery_state = "delivered"

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
                        address_string += ", " + record.partner_shipping_id.city_id.name
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
        if not self.depot_id:
            raise UserError(
                _("Depot missing on partner '%s'") % self.partner_shipping_id.name
            )

        if (
            abs(self.partner_shipping_id.partner_longitude) < 0.1
            and abs(self.partner_shipping_id.partner_latitude) < 0.1
        ):
            self.partner_shipping_id.geocode_one_partner_movetex()

        ICPSudo = self.env["ir.config_parameter"].sudo()
        extra_drop_duration = ICPSudo.get_param("flex_routes.extra_drop_duration")
        fixed_drop_duration_in_seconds = ICPSudo.get_param(
            "flex_routes.fixed_drop_duration_in_seconds"
        )
        variable_drop_duration_in_seconds = ICPSudo.get_param(
            "flex_routes.variable_drop_duration_in_seconds"
        )
        extra_drop_duration_in_seconds = ICPSudo.get_param(
            "flex_routes.extra_drop_duration_in_seconds"
        )
        payload = {
            "id": self.id,
            "destination": {
                "id": self.partner_shipping_id.id,
                "lon": self.partner_shipping_id.partner_longitude,
                "lat": self.partner_shipping_id.partner_latitude,
            },
            "deliveryWindow": {
                "startInSeconds": 25200,  # TODO
                "stopInSeconds": 64800,  # TODO
            },
            "depotId": self.depot_id.id,
            "preferredTransportationMode": "Car",  # TODO
            "allowedTransportationModes": "Car",  # TODO
            "revenue": 0,  # Ken wilt 0
            "priority": 10,  # TODO
            "duedate": self.date_order.isoformat(),
            "name": self.name,
            "dropSize": [self.total_crate_equivalence],
            "extraDropDuration": int(extra_drop_duration),  # TODO
            "fixedDropDurationInSeconds": int(fixed_drop_duration_in_seconds),  # TODO
            "variableDropDurationInSeconds": int(
                variable_drop_duration_in_seconds
            ),  # TODO
            "extraDropDurationInSeconds": int(extra_drop_duration_in_seconds),  # TODO
        }
        return payload
