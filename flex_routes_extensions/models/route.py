from odoo import api, fields, models


class RouteRoute(models.Model):
    _inherit = "route.route"

    route_picking_ids = fields.One2many("route.picking.line", "route_id")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.generate_route_picking_ids()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if vals.get("sale_order_ids", False):
            for record in self:
                record.generate_route_picking_ids()
        return res

    @api.multi
    @api.depends("sale_order_ids")
    def generate_route_picking_ids(self):
        self.ensure_one()
        RoutePicking = self.env["route.picking.line"]
        if self.route_picking_ids:
            self.route_picking_ids.unlink()
        for order in self.sale_order_ids:
            for line in order.order_line:
                route_picking = RoutePicking.search(
                    [
                        "&",
                        ("route_id", "=", self.id),
                        ("product_id", "=", line.product_id.id),
                    ]
                )
                if not route_picking:
                    route_picking = RoutePicking.create(
                        {"route_id": self.id, "product_id": line.product_id.id}
                    )
                route_picking.product_qty += line.product_uom_qty


class RouteOptimization(models.Model):
    _inherit = "route.optimization"

    @api.multi
    @api.depends("sale_order_ids", "date")
    def start_optimization(self):
        super().start_optimization()
        for route in self.route_ids:
            route.generate_route_picking_ids()
