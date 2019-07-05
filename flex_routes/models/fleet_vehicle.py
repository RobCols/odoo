from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vehicle_name = fields.Char("Voertuignaam")
    vehicle_type_id = fields.Char("Voertuig type-id")
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

    min_usage_time = fields.Float("Minimum gebruiksduur")
    max_usage_time = fields.Float("Maximum gebruiksduur")
    usage_window_start = fields.Integer("Start gebruiksvenster")
    usage_window_stop = fields.Integer("Stop gebruiksvenster")
    range_in_meter = fields.Integer("Afstand in meter")
    abs_range_in_meter = fields.Integer("Totale afstand in meter")
    range_in_meter_violation_weight = fields.Float(
        "Afstand in meter overtreding weight"
    )
    min_drops = fields.Integer("Minimum # leveringen")
    drop_weight = fields.Integer("Drop weight")
    distance_weight = fields.Float("Distance weight")
    usage_time_weight = fields.Float("Gebruiksduur weight")
    max_usage_time_violation_weight = fields.Float(
        "Max gebruiksduur overtreding weight"
    )
    usage_weight = fields.Integer("Gebruik weight")
    min_drops_violation_weight = fields.Integer("Min drops overtreding weight")
    min_usage_time_violation_weight = fields.Float(
        "Min gebruikstijd overtreding weight"
    )
    drop_duration_in_seconds = fields.Integer("Dropduur in seconden")
    multi_drop_duration_in_seconds = fields.Integer("Multi-drop duur in seconden")
    depot_stop_duration_in_seconds = fields.Integer("Depot-stop duur in seconden")
    priority_cost = fields.Integer("Prioriteitskost")
    travel_speed = fields.Integer("Reissnelheid")
    max_usages = fields.Integer("Maximum # inzetten")
    drop_duration_speed_factor = fields.Integer("Drop-duursnelheidsfactor")
    abs_range_in_drops = fields.Integer("Absolute capaciteit in leveringen")
    abs_range_in_drop_size = fields.Integer(
        "Absolute capaciteit in grootte per levering"
    )

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
