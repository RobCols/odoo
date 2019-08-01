from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # @api.multi
    # def _prepare_invoice(self):
    #     self.ensure_one()
    #     invoice_vals = super()._prepare_invoice()
    #     if self.partner_id.customer_type == "b2c":
    #         journal_id = self.env.ref("flex_sale_flows.delivery_notes")
    #         invoice_vals["journal_id"] = journal_id.id
    #     return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()
        self.update(
            self._get_purchase_price(
                self.order_id.pricelist_id,
                self.product_id,
                self.product_uom,
                self.order_id.date_order,
            )
        )

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        """
        sale_margin/models/sale_order.py
        https://github.com/odoo/odoo/blob/12.0/addons/sale_margin/models/sale_order.py#L26
        """
        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist.currency_id
        seller_ids = product.seller_ids.search(
            [
                "&",
                "|",
                ["date_start", "<=", date],
                ["date_start", "=", False],
                "|",
                ["date_end", ">", date],
                ["date_end", "=", False],
            ]
        ).sorted(key=lambda r: r.sequence)
        if not seller_ids:
            purchase_price = product.standard_price
        else:
            purchase_price = seller_ids[0].price
        if product_uom != product.uom_id:
            purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        price = frm_cur._convert(
            purchase_price,
            to_cur,
            self.order_id.company_id or self.env.user.company_id,
            date or fields.Date.today(),
            round=False,
        )
        return {"purchase_price": price}
