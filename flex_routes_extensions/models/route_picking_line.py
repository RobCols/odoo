from odoo import api, fields, models


class RoutePickingLine(models.Model):
    _name = "route.picking.line"
    _description = "Pickinglijn gebaseerd op een route"

    product_qty = fields.Integer("#")
    product_id = fields.Many2one("product.product", "Product")
    route_id = fields.Many2one("route.route")
    state = fields.Boolean("Picked", default=False)
    stock_location = fields.Char(related="product_id.stock_location")
