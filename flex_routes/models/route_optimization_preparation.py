from odoo import api, fields, models


class RouteOptimizationPreparation(models.Model):
    _name = "route.optimization.preparation"
    _description = "Optimalisatievoorbereiding"

    vehicle_id = fields.Many2one("fleet.vehicle", "Voertuig")
    user_id = fields.Many2one("res.users", "Chauffeur")
    optimization_id = fields.Many2one("route.optimization")
    min_driving_time = fields.Integer("Minimum rijtijd")
    max_driving_time = fields.Integer("Maximum rijtijd")

    @api.model
    def get_movetex_data(self):
        self.ensure_one()
        payload = self.vehicle_id.get_movetex_fields_as_json()
        payload.update(
            {
                "minUsageTime": self.min_driving_time,
                "maxUsageTime": self.max_driving_time,
            }
        )
        payload["vehicleId"] = f"{payload['vehicleId']}_{self.user_id.id}"
        return payload

    @api.multi
    @api.depends("vehicle_id", "user_id")
    def name_get(self):
        return [
            (r.id, (f"{r.vehicle_id.license_plate} ({r.user_id.display_name})"))
            for r in self
        ]
