from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order = fields.Datetime(related="order_id.date_order", store=True)

    def open_report(self, supplier_name, is_weekly=False):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"supplier_name": supplier_name, "is_weekly": is_weekly},
        }

        if is_weekly:
            return self.env.ref(
                "flex_reporting.action_report_forecasting_weekly"
            ).report_action(self, data)
        return self.env.ref(
            "flex_reporting.action_report_forecasting_daily"
        ).report_action(self, data)

    def get_daily_data(self):
        headers = []
        self.sorted(lambda i: i.date_order)
        for record in self:
            headers.append(record.date_order.date().strftime("%d/%m/%Y"))
        headers = list(set(headers))
        headers.sort()
        result = self.parse_report_data(headers)
        result = result["result"]
        grand_total = ["Grand Total"]
        for res in result:
            i = 1
            while i < len(headers) + 1:
                if res[i]:
                    if grand_total[i]:
                        grand_total[i] += res[i]
                    else:
                        grand_total.append(res[i])
                i += 1
        result.append(grand_total)
        result = {"headers": headers, "result": result}
        return result

    def parse_report_data(self, headers, is_weekly=False):
        result = {}
        for record in self:
            if not record.product_id.is_empty:
                if is_weekly:
                    index = headers.index("W" + record.date_order.isocalendar()[1]) + 1
                else:
                    index = (
                        headers.index(record.date_order.date().strftime("%d/%m/%Y")) + 1
                    )
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

        return {"result": result}

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
        result = self.parse_report_data(headers, True)
        result = result["result"]
        for res in result:
            while len(res) < len(headers) + 1:
                res.append("")
        result = {"headers": headers, "result": result}
        return result


class ForecastReportWeeklyWizard(models.TransientModel):
    _name = "forecast.wizard.weekly"

    start_date = fields.Date("Start date")
    week_count = fields.Integer("Number of weeks")
    supplier = fields.Many2one("res.partner", domain=[("supplier", "=", True)])

    def generate_report(self):
        if week_count < 0:
            raise UserError(_("Week count must be a positive number."))
        if not self.supplier:
            raise UserError(_("Supplier can't be empty."))
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
        return order_lines.open_report(self.supplier.display_name, True)


class ReportForecasting(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = "report.flex_reporting.forecasting_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order.line"].search([("id", "in", data["ids"])])

        if data["form"].get("is_weekly", False):
            report_lines = docs.get_weekly_data()
            report_headers = report_lines["headers"]
            report_lines = report_lines["result"]
        else:
            report_lines = docs.get_daily_data()
            report_headers = report_lines["headers"]
            report_lines = report_lines["result"]
        return {
            "doc_ids": docs.ids,
            "doc_model": data["model"],
            "supplier_name": data["form"]["supplier_name"],
            "docs": docs,
            "report_headers": report_headers,
            "report_lines": report_lines,
        }


class ForecastReportDailyWizard(models.TransientModel):
    _name = "forecast.wizard.daily"

    start_date = fields.Date()
    end_date = fields.Date()
    supplier = fields.Many2one("res.partner", domain=[("supplier", "=", True)])

    def generate_report(self):
        if self.end_date < self.start_date:
            raise UserError(_("End date must be after start date"))
        if not self.supplier:
            raise UserError(_("Supplier can't be empty"))

        sale_orders = self.env["sale.order"].search(
            [
                "&",
                ("date_order", ">=", self.start_date),
                ("date_order", "<=", self.end_date),
            ]
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
        l.append("W" + d[1])
    return sorted(set(l))
