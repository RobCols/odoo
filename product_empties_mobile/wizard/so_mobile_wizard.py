from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval


class SOMobileWizard(models.TransientModel):
    _name = "so.mobile.wizard"

    so_id = fields.Many2one(comodel_name="sale.order", string="Sale Order/Quotation")

    def open_so_mobile_old(self):
        """Open form view of selected sale order/quotation"""
        if not self.so_id:
            raise UserError(_("Please select Sale Order/Quotation."))
        action = self.env.ref(
            "product_empties_mobile.action_open_sale_order_mobile_view"
        ).read()
        if action:
            action = action[0]
        else:
            raise UserError(
                _(
                    "Sorry!! we are unable to proceed request "
                    "due to some error in system"
                )
            )
        context = safe_eval(action.get("context", {}))
        context["so_id"] = self.so_id.id
        context["active_id"] = self.so_id.id
        context["active_ids"] = [self.so_id.id]
        context["active_model"] = "sale.order"
        action["context"] = context

        return action

    def open_so_mobile_new(self):
        """Open blank form view to create new quotation"""
        action = self.env.ref(
            "product_empties_mobile.action_open_sale_order_mobile_view"
        ).read()
        if action:
            action = action[0]
        else:
            raise UserError(
                _(
                    "Sorry!! we are unable to proceed request "
                    "due to some error in system"
                )
            )
        context = safe_eval(action.get("context", {}))
        context["active_id"] = False
        context["active_ids"] = []
        context["active_model"] = "sale.order"
        return action
