from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vehicle_name = fields.Char()
    vehicle_type_id = fields.Char()
    start_location_partner_id = fields.Many2one("res.partner", "Startlocatie")
    start_location_lat = fields.Float(
        related="start_location_partner_id.partner_latitude"
    )
    start_location_lng = fields.Float(
        related="start_location_partner_id.partner_longitude"
    )
    stop_location_partner_id = fields.Many2one("res.partner", "Stoplocatie")
    stop_location_lat = fields.Float(
        related="stop_location_partner_id.partner_latitude"
    )
    stop_location_lng = fields.Float(
        related="stop_location_partner_id.partner_longitude"
    )

    depot_id = fields.Many2one("res.partner", "Depot")

    min_usage_time = fields.Float()
    max_usage_time = fields.Float()
    usage_window_start = fields.Integer()
    usage_window_stop = fields.Integer()
    range_in_meter = fields.Integer()
    abs_range_in_meter = fields.Integer()
    range_in_meter_violation_weight = fields.Float()
    min_drops = fields.Integer()
    drop_weight = fields.Integer()
    distance_weight = fields.Float()
    usage_time_weight = fields.Float()
    max_usage_time_violation_weight = fields.Float()
    usage_weight = fields.Integer()
    min_drops_violation_weight = fields.Integer()
    min_usage_time_violation_weight = fields.Float()
    drop_duration_in_seconds = fields.Integer()
    multi_drop_duration_in_seconds = fields.Integer()
    depot_stop_duration_in_seconds = fields.Integer()
    priority_cost = fields.Integer()
    travel_speed = fields.Integer()
    max_usages = fields.Integer()
    drop_duration_speed_factor = fields.Integer()
    abs_range_in_drops = fields.Integer()
    abs_range_in_drop_size = fields.Integer()

    @api.model
    def get_movetex_fields_as_json(self):
        self.ensure_one()
        payload = {
            "vehicleId": self.id,
            "vehicleName": self.vehicle_name,
            "vehicleTypeId": self.vehicle_type_id,
            "depotId": self.depot_id.id,
            "startLocation": {
                "id": self.start_location_partner_id.id,
                "lon": self.start_location_lng,
                "lat": self.start_location_lat,
            },
            "stopLocation": {
                "id": self.stop_location_partner_id.id,
                "lon": self.stop_location_lng,
                "lat": self.stop_location_lat,
            },
            "usageWindow": {
                "startInSeconds": self.usage_window_start,
                "stopInSeconds": self.usage_window_stop,
            },
            "minDrops": self.min_drops,
            "absRangeInDrops": self.abs_range_in_drops,
            "absRangeInDropSize": [self.abs_range_in_drop_size],
            "rangeInMeter": self.range_in_meter,
            "rangeInMeterViolationWeight": self.range_in_meter_violation_weight,
            "absRangeInmeter": self.abs_range_in_meter,
            "dropWeight": self.drop_weight,
            "distanceWeight": self.distance_weight,
            "usageTimeWeight": self.usage_time_weight,
            "maxUsageTimeViolationWeight": self.max_usage_time_violation_weight,
            "usageWeight": self.usage_weight,
            "minDropsViolationWeight": self.min_drops_violation_weight,
            "minUsageTimeViolationWeight": self.min_usage_time_violation_weight,
            "dropDurationInSeconds": self.drop_duration_in_seconds,
            "multiDropDurationInSeconds": self.multi_drop_duration_in_seconds,
            "depotStopDurationInSeconds": self.depot_stop_duration_in_seconds,
            "priorityCost": self.priority_cost,
            "travelSpeed": self.travel_speed,
            "maxUsages": self.max_usages,
            "dropDurationSpeedFactor": self.drop_duration_speed_factor,
        }
        return payload
