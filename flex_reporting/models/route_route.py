from odoo import api, fields, models


class RouteRoute(models.Model):
    _inherit = "route.route"
    name = fields.Char(compute="_compute_name")

    def print_picking(self):
        routes = self.env["route.route"].search([("date", "=", self.date)])
        return self.env.ref("flex_reporting.action_report_picking").report_action(
            routes
        )

    def _compute_name(self):
        for record in self:
            record.name = record.name_get()[0][1]

    @api.multi
    def get_picking_data_for_report(self):
        headers = ["Loc", "Product"]
        result = {}
        self.sorted(key=lambda i: i.letter)
        for record in self:
            headers.append(record.letter)
            for picking in record.route_picking_ids:
                result[picking.product_id.id] = [
                    picking.stock_location,
                    picking.product_id.name,
                ]

        for product_id in result:
            grand_total = 0
            for record in self:
                qty = 0
                pickings = record.route_picking_ids.filtered(
                    lambda r: r.product_id.id == product_id
                )
                for picking in pickings:
                    qty += picking.product_qty
                    grand_total += qty
                if not qty:
                    qty = ""
                result[product_id].append(qty)
            result[product_id].append(grand_total)
        headers.append("Grand Total")
        result = list(result.values())
        result.sort(key=lambda i: i[0])
        result = {"headers": headers, "values": result}
        return result
