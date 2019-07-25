from odoo import api, fields, models


class RouteOptimization(models.Model):
    _inherit = "route.optimization"

    def print_picking(self):
        self.ensure_one()
        return self.env.ref("flex_reporting.action_report_picking").report_action(
            self.route_ids
        )


class RouteRoute(models.Model):
    _inherit = "route.route"
    name = fields.Char(compute="_compute_name")
    total_crate_equivalence = fields.Float(compute="_compute_total_crate_equivalence")

    def _compute_name(self):
        for record in self:
            record.name = record.name_get()[0][1]

    @api.depends("sale_order_ids", "sale_order_ids.total_crate_equivalence")
    def _compute_total_crate_equivalence(self):
        for record in self:
            for so in record.sale_order_ids:
                record.total_crate_equivalence += so.total_crate_equivalence

    @api.multi
    def get_empty_data_for_report(self):
        self.sorted(key=lambda i: i.letter)
        headers = []
        result = {}
        index = 0
        for record in self:
            headers.append(record.letter)
            result[record.id] = [record.user_id.display_name]
            i = 0
            while i < index:
                result[record.id].append("")
                i += 1
            result[record.id].append(record.total_crate_equivalence)
            while len(result[record.id]) < len(self.ids) + 1:
                result[record.id].append("")
            index += 1
        result = list(result.values())
        return {"headers": headers, "empties": result}

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
