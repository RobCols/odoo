from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    company_address_id = fields.Many2one("res.partner", related="company_id.partner_id")

    def open_report(self):
        data = {"ids": self.ids, "model": self._name}
        return self.env.ref("flex_reporting.action_report_invoices").report_action(
            self, data
        )

    def get_invoice_data_for_report(self):
        result = {}
        self.sorted(key=lambda i: i.number)
        for record in self:
            total_empties = 0
            total_prod = 0
            total_prod_vat = 0
            six_pct_vat = 0
            twentyone_pct_vat = 0
            for line in record.invoice_line_ids:
                if line.product_id.is_empty:
                    total_empties += line.price_total
                else:
                    total_prod += line.price_subtotal
                    total_prod_vat += line.price_total
            total_price = total_prod_vat - total_empties
            result["record_id"] = {
                total_empties,
                total_prod,
                total_prod_vat,
                six_pct_vat,
                twentyone_pct_vat,
                total_price,
            }
        result = result.values()
        result = list(result)
        result.sort(key=lambda i: i[0]["values"][0])
        return result


class InvoiceReportWizard(models.TransientModel):
    _name = "report.wizard.invoice"

    start_date = fields.Date()
    end_date = fields.Date()

    def generate_report(self):
        if self.end_date < self.start_date:
            raise UserError(_("End date must be after start date"))
        invoices = self.env["account.invoice"].search(
            [
                "&",
                ("date_due", ">=", self.start_date),
                ("date_due", "<=", self.end_date),
            ]
        )

        return invoices.open_report(self.supplier.display_name)


class ReportAccountInvoice(models.AbstractModel):

    _name = "report.flex_reporting.invoice_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["account.invoice"].search([("id", "in", data["ids"])])
        report_lines = docs.get_invoice_data_for_report()
        return {
            "doc_ids": docs.ids,
            "doc_model": data["model"],
            "docs": docs,
            "report_lines": report_lines,
        }
