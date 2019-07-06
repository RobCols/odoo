from odoo import api, fields, models


class RoutePickingLine(models.Model):
    _name = "route.picking.line"
    _description = "Pickinglijn gebaseerd op een route"

    product_qty = fields.Integer("#")
    product_id = fields.Many2one("product.product", "Product")
    route_id = fields.Many2one("route.route")
    state = fields.Boolean("Ingeladen", default=False)
