from odoo import api, fields, models


class RoutePickingLine(models.Model):
    _name = "route.picking.line"
    _description = "Pickinglijn gebaseerd op een route"

    product_qty = fields.Integer("#")
    product_id = fields.Many2one("product.product", "Product")
    route_id = fields.Many2one("route.route")
    state = fields.Boolean("Picked", default=False)
    stock_location = fields.Char(related="product_id.stock_location")
    flex_color = fields.Integer(compute="_compute_flex_color")

    @api.depends("state")
    def _compute_flex_color(self):
        for record in self:
            if record.state:
                record.flex_color = 10
                continue
            record.flex_color = 2

    @api.multi
    def mark_as_picked(self):
        for record in self:
            record.state = not record.state
