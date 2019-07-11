from odoo import api, fields, models


class RouteRoute(models.Model):
    _inherit = "route.route"

    depot_latitude = fields.Float(compute="_compute_depot_coords")
    depot_longitude = fields.Float(compute="_compute_depot_coords")
    routing_zoomlevel = fields.Integer()
    @api.depends("vehicle_id", "vehicle_id.depot_id")
    def _compute_depot_coords(self):
        for record in self:
            if record.vehicle_id and record.vehicle_id.depot_id:
                record.depot_latitude = record.vehicle_id.depot_id.partner_latitude
                record.depot_longitude = record.vehicle_id.depot_id.partner_longitude
