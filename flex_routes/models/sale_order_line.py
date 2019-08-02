from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_state = fields.Selection([('undelivered', 'Nog niet afgeleverd'), ('delivered', 'Afgeleverd')])
    flex_color = fields.Integer(compute="_compute_flex_color")

    @api.depends("delivery_state")
    def _compute_flex_color(self):
        for record in self:
            if record.delivery_state == "delivered":
                record.flex_color = 10
                continue
            record.flex_color = 2


    @api.multi
    def set_delivery_state_to_delivered(self):
        self.ensure_one()
        self.delivery_state = "delivered"

    @api.multi
    def set_delivery_state_to_undelivered(self):
        self.ensure_one()
        self.delivery_state = "undelivered"
