from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_type = fields.Selection(
        [
            ("b2c", "B2C"),
            ("b2b_monthly", "B2B Monthly"),
            ("b2b_delivery", "B2B Delivery"),
        ]
    )

