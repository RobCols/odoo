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

    dropoff_zoomlevel = fields.Integer(default=20)
    dropoff_latitude = fields.Float(
        string="Geo Latitude", digits=(16, 5), compute="_compute_dropoff"
    )
    dropoff_longitude = fields.Float(
        string="Geo Longitude", digits=(16, 5), compute="_compute_dropoff"
    )

    @api.multi
    def button_set_dropoff_to_routing(self):
        for record in self:
            record.dropoff_latitude = record.partner_latitude
            record.dropoff_longitude = record.partner_longitude

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_dropoff(self):
        for record in self:
            if record.partner_latitude and record.partner_longitude:
                if record.dropoff_latitude and record.dropoff_longitude:
                    continue
                record.dropoff_latitude = record.partner_latitude
                record.dropoff_longitude = record.partner_longitude
