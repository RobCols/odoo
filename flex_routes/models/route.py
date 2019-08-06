from odoo import api, fields, models


class RouteRoute(models.Model):
    _name = "route.route"
    _description = "Routebeschrijving"

    user_id = fields.Many2one("res.users", "Chauffeur")
    date = fields.Date("Datum")
    vehicle_id = fields.Many2one("fleet.vehicle", "Voertuig")
    sale_order_ids = fields.One2many("sale.order", "route_id", "Order")
    optimization_id = fields.Many2one("route.optimization", "Optimalizatie")
    letter = fields.Char()

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
            "target": "current",
            "res_model": "sale.order",
            "active_ids": self.sale_order_ids.ids,
            "res_ids": self.sale_order_ids.ids,
            "ids": self.sale_order_ids.ids,
            "context": {
                "active_ids": self.sale_order_ids.ids,
                "res_ids": self.sale_order_ids.ids,
                "ids": self.sale_order_ids.ids,
                "hide_selectors": True,
                "form_view_initial_mode": "edit",
            },
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.sale_order_ids.ids)],
        }
