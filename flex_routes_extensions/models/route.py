from odoo import api, fields, models


class RouteRoute(models.Model):
    _inherit = "route.route"

    route_picking_ids = fields.One2many("route.picking.line", "route_id")
    route_loading_ids = fields.One2many("route.loading.line", "route_id")

    @api.multi
    @api.depends("sale_order_ids")
    def generate_route_loading_ids(self):
        self.ensure_one()
        if self.route_loading_ids:
            self.route_loading_ids.unlink()
        RouteLoading = self.env["route.loading.line"]
        for order in self.sale_order_ids:
            for line in order.order_line:
                if line.product_id and line.product_uom_qty > 0:
                    route_loading = RouteLoading.search(
                        [
                            "&",
                            "&",
                            ("route_id", "=", self.id),
                            ("product_id", "=", line.product_id.id),
                            ("order_id", "=", order.id),
                        ]
                    )
                    if not route_loading:
                        route_loading = RouteLoading.create(
                            {
                                "route_id": self.id,
                                "order_id": order.id,
                                "product_id": line.product_id.id,
                                "product_uom_qty": line.product_uom_qty,
                                "route_sequence": order.route_sequence,
                            }
                        )

    @api.multi
    @api.depends("sale_order_ids")
    def generate_route_picking_ids(self):
        self.ensure_one()
        RoutePicking = self.env["route.picking.line"]
        if self.route_picking_ids:
            self.route_picking_ids.unlink()
        for order in self.sale_order_ids:
            for line in order.order_line:
                if line.product_id and line.product_uom_qty > 0:
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
            route.generate_route_loading_ids()
