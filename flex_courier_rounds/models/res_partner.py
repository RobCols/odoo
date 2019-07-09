from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    delivery_dow = fields.Selection(
        string="Delivery Day Of Week",
        selection=[
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),
        ],
    )

    dropoff_zoomlevel = fields.Integer()
    dropoff_latitude = fields.Float(string="Geo Latitude", digits=(16, 5))
    dropoff_longitude = fields.Float(string="Geo Longitude", digits=(16, 5))

    @api.multi
    def button_set_dropoff_to_routing(self):
        for record in self:
            record.dropoff_latitude = record.partner_latitude
            record.dropoff_longitude = record.partner_longitude
