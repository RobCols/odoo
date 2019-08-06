from odoo import api, fields, models
from odoo.tools import safe_eval


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

    def open_map(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": f"/route/map?active_id={self.id}",
        }
        # action = self.env.ref(
        #     "flex_courier_rounds.action_open_map_view"
        # ).read()
        # if action:
        #     action = action[0]
        # context = safe_eval(action.get("context", {}))
        # context["active_id"] = self.id
        # context["active_ids"] = [self.id]
        # context["sale_order_ids"] = self.sale_order_ids.ids
        # context["active_model"] = "route.route"
        # context["depot_latitude"] = self.depot_latitude
        # context["depot_longitude"] = self.depot_longitude
        # action["context"] = context

        # return action
