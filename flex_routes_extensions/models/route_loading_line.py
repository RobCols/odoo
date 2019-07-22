from odoo import api, fields, models


class RouteLoadingLine(models.Model):
    _name = "route.loading.line"
    _description = "Houdt de gegevens bij voor het inladen van alle orders per route"

    order_id = fields.Many2one("sale.order", "Order")
    product_id = fields.Many2one("product.product", "Product")
    product_uom_qty = fields.Integer("Hoeveelheid")
    route_id = fields.Many2one("route.route", "Route")
    route_sequence = fields.Integer(related="order_id.route_sequence")
    state = fields.Boolean("Ingeladen", default=False)
    flex_color = fields.Integer(compute="_compute_flex_color")

    @api.depends("state")
    def _compute_flex_color(self):
        for record in self:
            if record.state:
                record.flex_color = 10
                continue
            record.flex_color = 2

    @api.multi
    def mark_as_loaded(self):
        for record in self:
            record.state = not record.state
