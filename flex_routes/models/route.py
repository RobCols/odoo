from odoo import api, fields, models


class RouteRoute(models.Model):
    _name = "route.route"
    _description = "Routebeschrijving"

    user_id = fields.Many2one("res.users", "Chauffeur")
    date = fields.Date("Datum")
    vehicle_id = fields.Many2one("fleet.vehicle", "Voertuig")
    sale_order_ids = fields.One2many("sale.order", "route_id", "Order")
    optimization_id = fields.Many2one("route.optimization", "Optimalizatie")

    @api.multi
    @api.depends("date", "user_id", "user_id.display_name")
    def name_get(self):
        return [(r.id, f"{r.user_id.display_name} - {r.date}") for r in self]

    @api.multi
    def open_orders(self):
        self.ensure_one()

        return {
            "name": "Orders",
            "views": [
                (
                    self.env.ref("flex_routes.flex_routes_sale_order_view_tree").id,
                    "list",
                ),
                (self.env.ref("flex_routes.flex_routes_sale_view_form").id, "form"),
            ],
            "target": "self",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.sale_order_ids.ids)],
            "flags": {
                "form": {"action_buttons": True, "options": {"clear_breadcrumbs": True}}
            },
        }
