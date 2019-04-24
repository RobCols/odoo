from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        self = self.with_context(do_not_add_empty_products=True)
        return super(SaleAdvancePaymentInv, self).create_invoices()
