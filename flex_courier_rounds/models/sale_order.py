from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_latitude = fields.Float(related="partner_shipping_id.partner_latitude")
    partner_longitude = fields.Float(related="partner_shipping_id.partner_longitude")
    routing_zoomlevel = fields.Integer()
