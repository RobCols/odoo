from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    flex_state = fields.Selection(
        [
            ("none", "Nog geen actie ondernomen"),
            ("loaded", "Ingeladen"),
            ("completed", "Geleverd"),
        ]
    )
