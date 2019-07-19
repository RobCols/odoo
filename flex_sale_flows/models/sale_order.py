from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        if self.partner_id.customer_type == "b2c":
            journal_id = self.env.ref("flex_sale_flows.delivery_notes")
            invoice_vals["journal_id"] = journal_id.id
        return invoice_vals
