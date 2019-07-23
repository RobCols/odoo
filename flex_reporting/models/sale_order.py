from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def open_report(self, supplier_name):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"supplier_name": supplier_name},
        }

        return self.env.ref("flex_reporting.action_report_orders").report_action(
            self, data
        )

    def get_order_data_for_report(self, supplier_name):
        result = {}
        self.sorted(key=lambda i: i.date_order)
        quantity_index = 1
        price_index = 2
        for record in self:
            order_lines = record.order_line.filtered(
                lambda ol: any(
                    ol.product_id.seller_ids.filtered(
                        lambda s: s.name.display_name == supplier_name
                    )
                )
            )
            if order_lines:
                total_qty = 0
                total_price = 0
                for ol in order_lines:
                    total_qty += ol.product_uom_qty
                    total_price += ol.price_total
                total_price = round(total_price, 2)
                if result.get(record.date_order, False):
                    result[record.date_order].append(
                        {
                            "values": [record.name, total_qty, total_price],
                            "style": "font-weight: 700; color: #ff9900; background: #fff4a3",
                        }
                    )
                    result[record.date_order].append(
                        {
                            "values": [
                                record.partner_id.display_name
                                + " Tel: "
                                + record.partner_shipping_id.mobile
                                if record.partner_shipping_id.mobile
                                else "" + " of " + record.partner_shipping_id.phone
                                if record.partner_shipping_id.phone
                                else "",
                                total_qty,
                                total_price,
                            ],
                            "style": "font-weight: 700",
                        }
                    )
                    for ol in order_lines:
                        result[record.date_order].append(
                            {"values": [ol.name, ol.product_uom_qty, ol.price_total]}
                        )
                    result[record.date_order][0]["values"][quantity_index] += total_qty
                    result[record.date_order][0]["values"][price_index] += total_price
                    result[record.date_order][0]["values"][price_index] = round(
                        result[record.date_order][0]["values"][price_index], 2
                    )
                else:
                    result[record.date_order] = [
                        {
                            "values": [
                                "Levering %s "
                                % record.date_order.date().strftime("%d/%m/%Y"),
                                total_qty,
                                total_price,
                            ],
                            "style": "font-weight: 700; background: #fe921f; color: #ffffff",
                        }
                    ]
                    result[record.date_order].append(
                        {
                            "values": [record.name, total_qty, total_price],
                            "style": "font-weight: 700; color: #ff9900; background: #fff4a3",
                        }
                    )
                    result[record.date_order].append(
                        {
                            "values": [
                                record.partner_id.display_name
                                + " Tel: "
                                + record.partner_shipping_id.mobile
                                if record.partner_shipping_id.mobile
                                else "" + " of " + record.partner_shipping_id.phone
                                if record.partner_shipping_id.phone
                                else "",
                                total_qty,
                                total_price,
                            ],
                            "style": "font-weight: 700",
                        }
                    )
                    for ol in order_lines:
                        result[record.date_order].append(
                            {"values": [ol.name, ol.product_uom_qty, ol.price_total]}
                        )
        result = list(result.values())
        return result


class OrderReportWizard(models.TransientModel):
    _name = "report.wizard.order"

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

        return sale_orders.open_report(self.supplier.display_name)


class ReportOrder(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = "report.flex_reporting.order_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order"].search([("id", "in", data["ids"])])
        report_lines = docs.get_order_data_for_report(data["form"]["supplier_name"])
        return {
            "doc_ids": docs.ids,
            "doc_model": data["model"],
            "supplier_name": data["form"]["supplier_name"],
            "docs": docs,
            "report_lines": report_lines,
        }
