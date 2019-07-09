from odoo import http, _
from odoo.http import request


class SaleOrderBarcodeController(http.Controller):
    @http.route(
        "/sale_order/product/scan_from_so_mobile_view", type="json", auth="user"
    )
    def scan_product_barcode_so_mobile_view(self, barcode, **kw):
        product = request.env["product.product"].search(
            [("barcode", "=", barcode)], limit=1
        )
        if not product:
            return {"warning": _("No product exist with this barcode.")}
        product_empty_ids = {
            empt_line.product_id.id: {
                "product_id": [empt_line.product_id.id, empt_line.product_id.name],
                "quantity": 0,
                "button_quantity": empt_line.quantity,
                "barcode": empt_line.product_id.barcode,
            }
            for empt_line in product.product_empty_ids
        }
        return {
            "id": product.id,
            "name": product.name,
            "is_empty": product.is_empty,
            "product_empty_ids": product_empty_ids,
            "is_manual_empty": product.is_manual_empty,
            "display_name": product.display_name,
            "barcode": product.barcode,
            "image": product.image,
        }

    @http.route("/sale_order/product/add_from_manual_button", type="json", auth="user")
    def scan_product_id_so_mobile_view(self, product_id, **kw):
        product = request.env["product.product"].browse(int(product_id))
        if not product:
            return {"warning": _("No product exist with this barcode.")}
        product_empty_ids = {
            empt_line.product_id.id: {
                "product_id": [empt_line.product_id.id, empt_line.product_id.name],
                "quantity": 0,
                "button_quantity": empt_line.quantity,
                "barcode": empt_line.product_id.barcode,
            }
            for empt_line in product.product_empty_ids
        }
        return {
            "id": product.id,
            "name": product.name,
            "is_empty": product.is_empty,
            "product_empty_ids": product_empty_ids,
            "is_manual_empty": product.is_manual_empty,
            "display_name": product.display_name,
            "barcode": product.barcode,
            "image": product.image,
        }

    @http.route("/update/sale_order/product_return", type="json", auth="user")
    def update_sale_order_product_return(
        self, order_id, sale_order_note, so_lines, partner_id=None, **kw
    ):
        try:
            order_id = int(order_id)
        except ValueError:
            res = self.create_new_sale_order(
                partner_id=partner_id, so_note=sale_order_note
            )
            if res.get("message", False) or res.get("error", False):
                return res
            elif res.get("order_id", False):
                order_id = res.get("order_id")
            else:
                return self.get_error_message(error=True)
        sale_order = request.env["sale.order"].browse(order_id)
        result = sale_order.update_sale_order(
            so_lines=so_lines, so_note=sale_order_note
        )
        if result:
            return self.get_error_message(message_type="success")
        return self.get_error_message(error=True)

    def create_new_sale_order(self, partner_id, so_note):
        if not partner_id:
            return self.get_error_message(message_type="not_exist_customer", error=True)
        else:
            vals = {"partner_id": partner_id, "note": so_note}
            try:
                order_id = self.env["res.partner"].create(vals)
            except Exception:
                return self.get_error_message(error=True)
            return {"order_id": order_id}

    def get_error_message(self, message_type=None, message=None, error=False):
        if not message:
            if message_type == "success":
                message = _("Sale order updated successfully")
            elif message_type == "not_exist_customer":
                message = _("Customer not exist!!")
            else:
                message = _(
                    "Request can not be completed due to some system error!\n"
                    "Please try after some time."
                )
        if error:
            return {"error": message}
        return {"message": message}
