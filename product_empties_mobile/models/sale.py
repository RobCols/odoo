from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def update_sale_order(self, so_lines, so_note):
        self.ensure_one()
        new_lines = []
        old_lines = []
        product_obj = self.env["product.product"]
        new_so_lines = self.env["sale.order.line"]
        for line_id in so_lines:
            if line_id.startswith("new"):
                new_lines.append(so_lines[line_id])
            else:
                old_lines.append(so_lines[line_id])
        if new_lines:
            for new_line in new_lines:
                product_id = new_line["product_id"][0]
                quantity = new_line["product_uom_qty"]
                try:
                    product_id = int(product_id)
                    product_id = product_obj.browse(product_id)
                    quantity = 0 - int(quantity)
                except Exception:
                    return False
                self = self.with_context(do_not_add_empty_products=True)
                order_line = self.add_update_empty_product_line(
                    product_id=product_id, quantity=quantity, do_not_update=True
                )
                new_so_lines |= order_line
        else:
            for old_line in old_lines:
                product_id = old_line["product_id"][0]
                quantity = old_line["product_uom_qty"]
                try:
                    product_id = int(product_id)
                    product_id = product_obj.browse(product_id)
                    quantity = 0 - int(quantity)
                except Exception:
                    return False
                if product_id.is_empty:
                    self = self.with_context(do_not_add_empty_products=True)
                    order_line = self.add_update_empty_product_line(
                        product_id=product_id, quantity=quantity, add=False
                    )
                    new_so_lines |= order_line
        if so_note:
            self.note = so_note
        if new_so_lines:
            return True
        return False
