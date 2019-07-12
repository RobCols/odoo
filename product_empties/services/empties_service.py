from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, ValidationError
import re


class EmptiesService(Component):
    _inherit = "base.rest.service"
    _name = "product.service"
    _usage = "empties"
    _collection = "product_empties.services"

    def _validator_total(self):
        return {
            "products": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "productId": {
                            "type": "integer",
                            "required": True,
                            "empty": False,
                        },
                        "quantity": {
                            "type": "integer",
                            "required": True,
                            "empty": False,
                        },
                    },
                },
            }
        }

    def _validator_return_total(self):
        return {"totalEmpties": {"type": "float"}}

    def total(self, products):
        total = 0.0
        for product in products:
            p = self.env["product.template"].browse(product["productId"])
            if p and p.product_empty_ids:
                for empty in p.product_empty_ids:
                    total += (
                        empty.product_id.lst_price
                        * empty.quantity
                        * product["quantity"]
                    )
        return {"totalEmpties": total}
