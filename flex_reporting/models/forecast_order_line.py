from odoo import api, fields, models
import datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(related="order_id.date_order", store=True)

    def open_report(self, supplier):
        datas = {
            "ids": self.ids,
            "model": "sale.order.line",
            "form": {"supplier": supplier},
            "docs": self,
        }
        return self.env.ref("flex_reporting.action_report_forecasting").report_action(
            self  # , data=datas
        )

    def get_weekly_data(self):
        start_date = False
        end_date = False
        for record in self:
            if not start_date:
                start_date = record.date_order.date()
            elif record.date_order.date() < start_date:
                start_date = record.date_order.date()
            if not end_date:
                end_date = record.date_order.date()
            elif record.date_order.date() > end_date:
                end_date = record.date_order.date()

        headers = find_weeks(start_date, end_date)
        result = {}
        supplier_names = []
        for record in self:
            if not record.product_id.is_empty:
                for supplier in record.product_id.seller_ids:
                    supplier_names.append(supplier.name.display_name)
                week = record.date_order.isocalendar()[1]
                index = headers.index(week) + 1
                if (
                    result.get(record.product_id.id)
                    and len(result.get(record.product_id.id)) >= index + 1
                ):
                    if type(result[record.product_id.id][index]) == type("a"):
                        result[record.product_id.id][index] = record.product_uom_qty
                    else:
                        result[record.product_id.id][index] += record.product_uom_qty
                elif result.get(record.product_id.id, False):
                    result[record.product_id.id].append(record.product_uom_qty)
                else:
                    result[record.product_id.id] = [record.product_id.name]
                    i = 1
                    while i < index:
                        result[record.product_id.id].append("")
                        i += 1
                    result[record.product_id.id].append(record.product_uom_qty)
        result = list(result.values())
        for res in result:
            while len(res) < len(headers) + 1:
                res.append("")
        result.sort(key=lambda i: i[0])
        result = {
            "headers": headers,
            "result": result,
            "supplier": max(set(supplier_names), key=supplier_names.count),
        }
        return result


class ForecastReportWizard(models.TransientModel):
    _name = "forecast.wizard"

    start_date = fields.Date("Start date")
    week_count = fields.Integer("Number of weeks")
    supplier = fields.Many2one("res.partner", domain=[("supplier", "=", True)])

    def generate_report(self):
        end_date = self.start_date + datetime.timedelta(weeks=self.week_count)
        sale_orders = self.env["sale.order"].search(
            ["&", ("date_order", ">=", self.start_date), ("date_order", "<=", end_date)]
        )

        order_lines = self.env["sale.order.line"].search(
            [("order_id", "in", sale_orders.ids)]
        )
        order_lines = order_lines.filtered(
            lambda ol: any(
                ol.product_id.seller_ids.filtered(
                    lambda s: s.name.id == self.supplier.id
                )
            )
        )
        return order_lines.open_report(self.supplier.display_name)


def find_weeks(start, end):
    l = []
    date_range = range((end - start).days + 1)
    for i in date_range:
        d = (start + datetime.timedelta(days=i)).isocalendar()
        l.append(d[1])
    return sorted(set(l))
